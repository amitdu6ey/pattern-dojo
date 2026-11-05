#!/usr/bin/env python3
"""Compile and run C++ with time and memory limits.

Shared by tools/build.py and the local judge (tools/serve.py). Standard library only.

Memory: macOS ignores RLIMIT_AS, so a watchdog polls the child's resident size and kills it once it passes the
limit. The reported peak comes from wait4()'s ru_maxrss (bytes on macOS, kilobytes elsewhere).

  python3 tools/runner.py --selftest
"""
import contextlib
import ctypes
import os
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time

CXX = os.environ.get("CXX", "g++")
CXXFLAGS = ["-std=c++17", "-O2", "-pipe"]
POLL_S = 0.005
OUTPUT_CAP = 1 << 20  # bytes of stdout kept and allowed
MB = 1024 * 1024


@contextlib.contextmanager
def workdir():
    """A fresh temp directory that is always removed afterwards."""
    d = tempfile.mkdtemp(prefix="dojo-")
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


def compile_cpp(sources, out_path, include_dirs=(), timeout=60):
    """Compile with g++ -std=c++17 -O2. Returns (ok, message). The message is the compiler output."""
    cmd = [CXX] + CXXFLAGS + ["-I" + d for d in include_dirs] + ["-o", out_path] + list(sources)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, "compiler timed out"
    except FileNotFoundError:
        return False, "compiler not found: " + CXX
    return p.returncode == 0, p.stderr.strip()


# ---- resident size of a running process -------------------------------------------------------------------

class _TaskInfo(ctypes.Structure):  # struct proc_taskinfo from <sys/proc_info.h>
    _fields_ = [("virtual_size", ctypes.c_uint64), ("resident_size", ctypes.c_uint64),
                ("total_user", ctypes.c_uint64), ("total_system", ctypes.c_uint64),
                ("threads_user", ctypes.c_uint64), ("threads_system", ctypes.c_uint64)] + [
        (n, ctypes.c_int32) for n in ("policy", "faults", "pageins", "cow_faults", "messages_sent",
                                      "messages_received", "syscalls_mach", "syscalls_unix", "csw",
                                      "threadnum", "numrunning", "priority")]


_libproc = None
if sys.platform == "darwin":
    try:
        _libproc = ctypes.CDLL("libproc.dylib")
    except OSError:
        _libproc = None


def current_rss(pid):
    """Resident size in bytes of a running process, or None if it cannot be read."""
    if _libproc is not None:
        info = _TaskInfo()
        n = _libproc.proc_pidinfo(pid, 4, 0, ctypes.byref(info), ctypes.sizeof(info))  # 4 = PROC_PIDTASKINFO
        return info.resident_size if n == ctypes.sizeof(info) else None
    try:
        with open("/proc/%d/statm" % pid) as f:
            return int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError, IndexError):
        pass
    try:
        out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
        return int(out) * 1024 if out else None
    except (OSError, ValueError):
        return None


# ---- running ----------------------------------------------------------------------------------------------

def run_exe(exe, stdin_text="", time_limit_ms=2000, memory_limit_mb=256, output_cap=OUTPUT_CAP):
    """Run a compiled program under limits and return a dict:

    status      OK, TLE, MLE, RE (crash or non-zero exit) or OLE (too much output)
    stdout      up to output_cap bytes, decoded
    stderr      up to 4000 characters
    cpu_ms      user plus system CPU time
    wall_ms     wall-clock time
    peak_mb     peak resident memory from ru_maxrss
    exit_code   exit code, or None if killed by a signal
    signal      signal number, or None
    """
    tmp = tempfile.mkdtemp(prefix="dojo-run-")
    try:
        in_path, out_path, err_path = (os.path.join(tmp, n) for n in ("in", "out", "err"))
        with open(in_path, "w") as f:
            f.write(stdin_text)
        cpu_cap = int(time_limit_ms / 1000.0) + 2

        def limits():  # runs in the child before exec
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_cap, cpu_cap + 1))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            resource.setrlimit(resource.RLIMIT_FSIZE, (output_cap + 1, output_cap + 1))

        with open(in_path, "rb") as fi, open(out_path, "wb") as fo, open(err_path, "wb") as fe:
            p = subprocess.Popen([exe], stdin=fi, stdout=fo, stderr=fe, cwd=tmp, preexec_fn=limits, close_fds=True)

        limit_bytes = int(memory_limit_mb * MB)
        start = time.perf_counter()
        deadline = start + time_limit_ms / 1000.0
        killed = None
        while True:
            done, status, ru = os.wait4(p.pid, os.WNOHANG)
            if done:
                break
            if time.perf_counter() >= deadline:
                killed = "TLE"
            else:
                rss = current_rss(p.pid)
                if rss is not None and rss > limit_bytes:
                    killed = "MLE"
            if killed:
                try:
                    os.kill(p.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                _, status, ru = os.wait4(p.pid, 0)
                break
            time.sleep(POLL_S)
        wall_ms = (time.perf_counter() - start) * 1000.0

        if os.WIFEXITED(status):
            code, sig = os.WEXITSTATUS(status), None
        else:
            code, sig = None, os.WTERMSIG(status)
        p.returncode = code if code is not None else -sig  # we reaped it ourselves
        peak = ru.ru_maxrss * (1 if sys.platform == "darwin" else 1024)
        cpu_ms = (ru.ru_utime + ru.ru_stime) * 1000.0
        out_size = os.path.getsize(out_path)

        if killed:
            verdict = killed
        elif sig == signal.SIGXFSZ or out_size > output_cap:
            verdict = "OLE"
        elif sig == signal.SIGXCPU:
            verdict = "TLE"
        elif sig is not None or code != 0:
            verdict = "RE"
        elif cpu_ms > time_limit_ms:
            verdict = "TLE"
        elif peak > limit_bytes:
            verdict = "MLE"
        else:
            verdict = "OK"

        with open(out_path, "rb") as f:
            stdout = f.read(output_cap).decode("utf-8", "replace")
        with open(err_path, "rb") as f:
            stderr = f.read(4000).decode("utf-8", "replace")
        return {"status": verdict, "stdout": stdout, "stderr": stderr, "cpu_ms": cpu_ms, "wall_ms": wall_ms,
                "peak_mb": peak / MB, "exit_code": code, "signal": sig}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def same_output(expected, actual):
    """Token-wise comparison, so trailing spaces and newlines do not matter."""
    return expected.split() == actual.split()


# ---- self-test --------------------------------------------------------------------------------------------

_SNIPPETS = {
    "sum": ('#include <iostream>\nint main(){ long long a,b; std::cin>>a>>b; std::cout<<a+b<<"\\n"; }\n', "3 4\n"),
    "spin": ("int main(){ volatile unsigned long x=0; while(true) x++; }\n", ""),
    "hog": ('#include <cstdio>\n#include <cstdlib>\n#include <cstring>\n'
            "static char* keep[1024];\n"
            "int main(){ for(int i=0;i<600;i++){ char*p=(char*)malloc(1<<20); if(!p) return 2; memset(p,1,1<<20); keep[i]=p; }\n"
            '  printf("%d\\n", keep[5][7]); }\n', ""),
    "touch64": ('#include <cstdio>\n#include <cstdlib>\n'
                "int main(){ size_t n=64u<<20; volatile char*p=(volatile char*)malloc(n);\n"
                "  for(size_t i=0;i<n;i+=4096) p[i]=1;  // volatile writes cannot be optimised away\n"
                '  printf("%d\\n", p[n/2]); }\n', ""),
    "crash": ("int main(){ volatile int* p=nullptr; *p=1; }\n", ""),
    "exit3": ("int main(){ return 3; }\n", ""),
    "flood": ('#include <cstdio>\nint main(){ while(true) puts("xxxxxxxxxxxxxxxxxxxxxxxx"); }\n', ""),
    "broken": ("int main( { }\n", ""),
}


def _selftest():
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print("%-4s %-34s %s" % ("PASS" if ok else "FAIL", name, detail))

    with workdir() as d:
        def build(key):
            src = os.path.join(d, key + ".cpp")
            with open(src, "w") as f:
                f.write(_SNIPPETS[key][0])
            exe = os.path.join(d, key)
            ok, msg = compile_cpp([src], exe)
            return ok, msg, exe

        ok, msg, exe = build("sum")
        r = run_exe(exe, _SNIPPETS["sum"][1])
        check("OK: reads input, prints 7", ok and r["status"] == "OK" and same_output("7", r["stdout"]),
              "%.0f ms, %.1f MB" % (r["wall_ms"], r["peak_mb"]))

        ok, msg, exe = build("spin")
        r = run_exe(exe, "", time_limit_ms=300)
        check("TLE: infinite loop is killed", ok and r["status"] == "TLE" and r["wall_ms"] < 1500, "%.0f ms" % r["wall_ms"])

        ok, msg, exe = build("hog")
        r = run_exe(exe, "", time_limit_ms=5000, memory_limit_mb=128)
        check("MLE: 600 MB request stopped near 128 MB", ok and r["status"] == "MLE" and r["peak_mb"] < 400,
              "peak %.0f MB, %.0f ms" % (r["peak_mb"], r["wall_ms"]))

        ok, msg, exe = build("touch64")
        r = run_exe(exe, "", memory_limit_mb=256)
        check("Memory is measured (64 MB program reads 64 to 100 MB)", ok and r["status"] == "OK" and 64 <= r["peak_mb"] <= 100,
              "peak %.1f MB" % r["peak_mb"])

        r = run_exe(exe, "", memory_limit_mb=32)
        check("MLE: peak above the limit is caught", r["status"] == "MLE", "limit 32 MB, peak %.1f MB" % r["peak_mb"])

        ok, msg, exe = build("crash")
        r = run_exe(exe)
        check("RE: crash is reported", ok and r["status"] == "RE" and r["signal"] is not None, "signal %s" % r["signal"])

        ok, msg, exe = build("exit3")
        r = run_exe(exe)
        check("RE: non-zero exit is reported", ok and r["status"] == "RE" and r["exit_code"] == 3, "exit %s" % r["exit_code"])

        ok, msg, exe = build("flood")
        r = run_exe(exe, "", time_limit_ms=3000, output_cap=65536)
        check("OLE: endless output is stopped", ok and r["status"] == "OLE", "%d bytes kept" % len(r["stdout"]))

        ok, msg, exe = build("broken")
        check("CE: syntax error gives a message", (not ok) and "error" in msg.lower(), msg.splitlines()[0][:60] if msg else "")

    n_ok = sum(results)
    print("\n%d of %d checks passed" % (n_ok, len(results)))
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
