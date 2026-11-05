#!/usr/bin/env python3
"""Check (and later build) the problems. Standard library only. See tools/FORMAT.md for the gates.

  python3 tools/build.py --check                  # every folder in problems/
  python3 tools/build.py --check pair-sum         # only the named problem ids
  python3 tools/build.py --check --root tools/fixtures

Gate 1: the reference passes every hand case and every scale case inside the limits.
Gate 2: the brute force agrees with the reference on all hand cases and on the fuzz inputs.
Gate 3 (scale tests defeat the brute force) and writing site/ arrive in P0.1d.
Exit status is 0 only if every problem passes.
"""
import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gens  # noqa: E402
import problem  # noqa: E402
import runner  # noqa: E402

MAX_ERRORS = 5  # per gate, so one broken program does not flood the output


def _compile(problem_dir, which, work):
    """Compile driver.cpp against <which>.cpp copied in as solution.cpp. Returns (exe or None, message)."""
    d = os.path.join(work, which)
    os.makedirs(d)
    shutil.copy(os.path.join(problem_dir, "driver.cpp"), os.path.join(d, "driver.cpp"))
    shutil.copy(os.path.join(problem_dir, which + ".cpp"), os.path.join(d, "solution.cpp"))
    exe = os.path.join(d, "run")
    ok, msg = runner.compile_cpp([os.path.join(d, "driver.cpp")], exe, include_dirs=[d])
    return (exe if ok else None), msg


def _short(text, n=40):
    text = " ".join(text.split())
    return text if len(text) <= n else text[:n] + "..."


def check_problem(path):
    """Run the gates on one problem folder. Returns {"id", "errors": [...], "info": "...", "scale": [...]}."""
    pid = os.path.basename(os.path.normpath(path))
    result = {"id": pid, "errors": [], "info": "", "scale": []}
    errs = result["errors"]

    fmt = problem.validate(path)
    if fmt:
        errs.extend("format: " + e for e in fmt)
        return result
    p, t = problem.load(path)
    tl, ml = p["time_limit_ms"], p["memory_limit_mb"]

    with runner.workdir() as work:
        ref_exe, msg = _compile(path, "solution", work)
        if ref_exe is None:
            errs.append("gate 1: reference does not compile: " + _short(msg, 200))
            return result
        brute_exe, msg = _compile(path, "brute", work)
        if brute_exe is None:
            errs.append("gate 2: brute force does not compile: " + _short(msg, 200))
            return result

        # ---- gate 1: the reference
        slowest = 0.0
        for case in t["cases"]:
            r = runner.run_exe(ref_exe, case["input"], tl, ml)
            if r["status"] != "OK":
                errs.append("gate 1: reference %s on case %r" % (r["status"], case["name"]))
            elif not runner.same_output(case["expected"], r["stdout"]):
                errs.append("gate 1: case %r expects %r but the reference printed %r"
                            % (case["name"], _short(case["expected"]), _short(r["stdout"])))
            slowest = max(slowest, r["wall_ms"])
        for s in t.get("scale", []):
            r = runner.run_exe(ref_exe, gens.generate(s["spec"]), tl, ml)
            if r["status"] != "OK":
                errs.append("gate 1: reference %s on scale test %r (limits %d ms, %d MB; used %.0f ms, %.0f MB)"
                            % (r["status"], s["name"], tl, ml, r["wall_ms"], r["peak_mb"]))
            else:
                result["scale"].append({"name": s["name"], "wall_ms": r["wall_ms"], "peak_mb": r["peak_mb"]})
            slowest = max(slowest, r["wall_ms"])
        if errs:
            errs[:] = errs[:MAX_ERRORS]
            errs.append("gate 2 skipped because gate 1 failed")
            return result

        # ---- gate 2: the brute force agrees with the reference
        for case in t["cases"]:
            r = runner.run_exe(brute_exe, case["input"], tl, ml)
            if r["status"] != "OK":
                errs.append("gate 2: brute force %s on case %r" % (r["status"], case["name"]))
            elif not runner.same_output(case["expected"], r["stdout"]):
                errs.append("gate 2: brute force prints %r on case %r, expected %r"
                            % (_short(r["stdout"]), case["name"], _short(case["expected"])))
        fuzz = gens.fuzz_inputs(t["fuzz"])
        for i, text in enumerate(fuzz):
            if len(errs) >= MAX_ERRORS:
                break
            a = runner.run_exe(ref_exe, text, tl, ml)
            b = runner.run_exe(brute_exe, text, tl, ml)
            if a["status"] != "OK" or b["status"] != "OK":
                errs.append("gate 2: fuzz input %d: reference %s, brute force %s" % (i, a["status"], b["status"]))
            elif not runner.same_output(a["stdout"], b["stdout"]):
                errs.append("gate 2: fuzz input %d: reference prints %r, brute force prints %r (input: %r)"
                            % (i, _short(a["stdout"]), _short(b["stdout"]), _short(text, 60)))
        errs[:] = errs[:MAX_ERRORS]

    if not errs:
        result["info"] = "%d cases, %d scale (slowest %.0f ms); brute agrees on %d cases + %d fuzz" % (
            len(t["cases"]), len(t.get("scale", [])), slowest, len(t["cases"]), len(fuzz))
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="problem ids to check (default: all)")
    ap.add_argument("--check", action="store_true", help="test only; write nothing")
    ap.add_argument("--root", help="folder that holds the problem folders (default: problems/)")
    args = ap.parse_args(argv)

    dirs = problem.problem_dirs(args.root)
    if args.ids:
        wanted = set(args.ids)
        missing = wanted - {os.path.basename(d) for d in dirs}
        if missing:
            print("unknown problem id(s): " + ", ".join(sorted(missing)))
            return 1
        dirs = [d for d in dirs if os.path.basename(d) in wanted]
    if not dirs:
        print("no problems found")
        return 0

    failed = 0
    for d in dirs:
        r = check_problem(d)
        print("%s %-28s %s" % ("ok  " if not r["errors"] else "FAIL", r["id"], r["info"]))
        for e in r["errors"]:
            print("     - " + e)
        failed += bool(r["errors"])
    if not args.check:
        print("(writing site/ arrives in P0.1d; the checks above are the same)")
    print("%d of %d problems pass" % (len(dirs) - failed, len(dirs)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
