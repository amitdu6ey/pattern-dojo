#!/usr/bin/env python3
"""Run every check that must pass before a commit. Standard library only.

  python3 tools/gate.py

Exit status is 0 only if every step passes, and it stops at the first failure. Always commit like this, in one chain:

  python3 tools/gate.py && git add -A && git commit -m "..." && git push origin main

so a failing gate can never be followed by a commit.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
STEPS = [
    ("unit tests", [PY, "-m", "unittest", "discover", "-s", "tools", "-p", "test_*.py"]),
    ("runner self-test", [PY, "tools/runner.py", "--selftest"]),
    ("fixture check", [PY, "tools/build.py", "--check", "--root", "tools/fixtures"]),
    ("problem check", [PY, "tools/build.py", "--check"]),
    ("site build", [PY, "tools/build.py"]),
]


def run(steps=STEPS, cwd=ROOT):
    """Run the steps in order. Returns 0 if all pass, otherwise 1 after the first failure."""
    for name, cmd in steps:
        start = time.time()
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        ok = p.returncode == 0
        print("%s %-18s %5.1fs" % ("ok  " if ok else "FAIL", name, time.time() - start), flush=True)
        if not ok:
            print((p.stdout + p.stderr).strip()[-3000:])
            print("gate FAILED at: " + name)
            return 1
    print("gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
