#!/usr/bin/env python3
"""Check and build the problems. Standard library only. See tools/FORMAT.md for the gates.

  python3 tools/build.py --check                  # test every folder in problems/, write nothing
  python3 tools/build.py                          # test, then write site/problems/ and site/data/ if all pass
  python3 tools/build.py --check pair-sum         # only the named problem ids
  python3 tools/build.py --check --root tools/fixtures

Gate 1: the reference passes every hand case and every scale case inside the limits.
Gate 2: the brute force agrees with the reference on all hand cases and on the fuzz inputs.
Gate 3: for each enforced dimension the brute force fails a scale test (TLE for time, MLE for space), and the
        reference stays under half of each enforced limit on the scale tests.
Exit status is 0 only if every problem passes. The site is written only when every problem passes.
"""
import argparse
import html
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import gens  # noqa: E402
import problem  # noqa: E402
import runner  # noqa: E402

MAX_ERRORS = 5  # per problem, so one broken program does not flood the output


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


def reference_headroom_errors(scale_results, time_limit_ms, memory_limit_mb, enforce):
    """Gate 3, part 1: on scale tests the reference must stay under half of each enforced limit."""
    errs = []
    for s in scale_results:
        if enforce.get("time") and s["wall_ms"] > time_limit_ms / 2.0:
            errs.append("gate 3: the reference needs %.0f ms on scale test %r, over half of the %d ms limit; "
                        "shrink the scale test or raise the limit" % (s["wall_ms"], s["name"], time_limit_ms))
        if enforce.get("space") and s["peak_mb"] > memory_limit_mb / 2.0:
            errs.append("gate 3: the reference peaks at %.0f MB on scale test %r, over half of the %d MB limit; "
                        "shrink the scale test or raise the limit" % (s["peak_mb"], s["name"], memory_limit_mb))
    return errs


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
    enforce = p["enforce"]
    scale_specs = t.get("scale", [])

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
        scale_inputs = []
        for s in scale_specs:
            text = gens.generate(s["spec"])
            scale_inputs.append(text)
            r = runner.run_exe(ref_exe, text, tl, ml)
            if r["status"] != "OK":
                errs.append("gate 1: reference %s on scale test %r (limits %d ms, %d MB; used %.0f ms, %.0f MB)"
                            % (r["status"], s["name"], tl, ml, r["wall_ms"], r["peak_mb"]))
            else:
                result["scale"].append({"name": s["name"], "wall_ms": r["wall_ms"], "peak_mb": r["peak_mb"]})
            slowest = max(slowest, r["wall_ms"])
        if errs:
            del errs[MAX_ERRORS - 1:]  # leave room for the note
            errs.append("gates 2 and 3 skipped because gate 1 failed")
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
        if errs:
            del errs[MAX_ERRORS - 1:]  # leave room for the note
            errs.append("gate 3 skipped because gate 2 failed")
            return result

        # ---- gate 3: the scale tests make the intended complexity necessary
        errs.extend(reference_headroom_errors(result["scale"], tl, ml, enforce))
        brute_runs = [(s["name"], runner.run_exe(brute_exe, text, tl, ml)) for s, text in zip(scale_specs, scale_inputs)]
        seen = {name: r["status"] for name, r in brute_runs}
        notes = []
        for dim, bad_status in (("time", "TLE"), ("space", "MLE")):
            if not enforce[dim]:
                notes.append("%s not enforced (%s)" % (dim, _short(enforce.get(dim + "_reason", ""), 50)))
                continue
            hits = [n for n, st in seen.items() if st == bad_status]
            if hits:
                notes.append("brute %s on %s" % (bad_status, ", ".join(repr(h) for h in hits[:2])))
            else:
                errs.append("gate 3: tests do not enforce the intended complexity (%s): the brute force never hit %s on a "
                            "scale test; it got %s" % (dim, bad_status, ", ".join("%s on %r" % (st, n) for n, st in seen.items())
                                                       or "no scale tests"))
        del errs[MAX_ERRORS:]

    if not errs:
        result["info"] = "%d cases, %d scale (slowest %.0f ms); brute agrees on %d cases + %d fuzz; %s" % (
            len(t["cases"]), len(scale_specs), slowest, len(t["cases"]), len(fuzz), "; ".join(notes))
    return result


# ---- site output ----------------------------------------------------------------------------------------------

def write_site(problem_dirs, out_dir):
    """Write a stub page per problem and an index of all problems. Real templates arrive in P0.3."""
    index = []
    for d in problem_dirs:
        p, _ = problem.load(d)
        page_dir = os.path.join(out_dir, "problems", p["id"])
        os.makedirs(page_dir, exist_ok=True)
        with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><title>%s</title></head>\n"
                    "<body><h1>%s</h1><p>%s</p><p><em>The full problem page arrives with the page template (P0.3).</em></p></body></html>\n"
                    % (html.escape(p["title"]), html.escape(p["title"]), html.escape(p["statement"])))
        index.append({k: p.get(k) for k in ("id", "title", "pattern", "tags", "difficulty", "level")})
    os.makedirs(os.path.join(out_dir, "data"), exist_ok=True)
    with open(os.path.join(out_dir, "data", "problems.json"), "w", encoding="utf-8") as f:
        json.dump({"problems": index}, f, indent=2)
        f.write("\n")
    return len(index)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="problem ids to check (default: all)")
    ap.add_argument("--check", action="store_true", help="test only; write nothing")
    ap.add_argument("--root", help="folder that holds the problem folders (default: problems/)")
    ap.add_argument("--out", default=os.path.join(ROOT, "site"), help="where the site is written (default: site/)")
    args = ap.parse_args(argv)

    dirs = problem.problem_dirs(args.root)
    if args.ids:
        wanted = set(args.ids)
        missing = wanted - {os.path.basename(d) for d in dirs}
        if missing:
            print("unknown problem id(s): " + ", ".join(sorted(missing)))
            return 1
        dirs = [d for d in dirs if os.path.basename(d) in wanted]

    failed = 0
    for d in dirs:
        r = check_problem(d)
        print("%s %-28s %s" % ("ok  " if not r["errors"] else "FAIL", r["id"], r["info"]))
        for e in r["errors"]:
            print("     - " + e)
        failed += bool(r["errors"])
    if dirs:
        print("%d of %d problems pass" % (len(dirs) - failed, len(dirs)))
    else:
        print("no problems found")
    if failed:
        return 1
    if not args.check:
        n = write_site(dirs, args.out)
        print("wrote %d problem page(s) and data/problems.json to %s" % (n, os.path.relpath(args.out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
