"""Tests for tools/build.py (gates 1 to 3 and the site output), using copies of the fixture problem with deliberate faults.

  python3 -m unittest discover -s tools -p "test_*.py"
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build  # noqa: E402

FIXTURE = os.path.join(HERE, "fixtures", "pair-sum")


class BuildGateTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="dojo-build-")
        self.dir = os.path.join(self.root, "pair-sum")
        shutil.copytree(FIXTURE, self.dir)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def edit(self, name, old, new):
        path = os.path.join(self.dir, name)
        with open(path) as f:
            text = f.read()
        self.assertIn(old, text)
        with open(path, "w") as f:
            f.write(text.replace(old, new, 1))

    def run_check(self):
        return build.check_problem(self.dir)

    def test_fixture_passes(self):
        r = self.run_check()
        self.assertEqual(r["errors"], [])
        self.assertIn("brute agrees", r["info"])
        self.assertEqual(len(r["scale"]), 1)

    def test_wrong_reference_fails_gate_1(self):
        self.edit("solution.cpp", "pairs += it->second;", "pairs += it->second + 1;")
        errs = self.run_check()["errors"]
        self.assertTrue(any(e.startswith("gate 1") and "expects" in e for e in errs), errs)
        self.assertTrue(any("gates 2 and 3 skipped" in e for e in errs), errs)

    def relax_walkthrough(self):
        """Point every walkthrough step at line 1, so a shorter solution.cpp still passes the format check."""
        path = os.path.join(self.dir, "problem.json")
        with open(path) as f:
            data = json.load(f)
        for step in data["walkthrough"]:
            step["lines"] = [1, 1]
        with open(path, "w") as f:
            json.dump(data, f)

    def test_slow_reference_fails_gate_1_on_scale(self):
        shutil.copy(os.path.join(self.dir, "brute.cpp"), os.path.join(self.dir, "solution.cpp"))
        self.relax_walkthrough()
        errs = self.run_check()["errors"]
        self.assertTrue(any("TLE on scale test" in e for e in errs), errs)

    def test_reference_that_does_not_compile(self):
        self.edit("solution.cpp", "long long pairs = 0;", "long long pairs = 0 int;")
        errs = self.run_check()["errors"]
        self.assertTrue(any("does not compile" in e for e in errs), errs)

    def test_wrong_brute_force_fails_gate_2(self):
        self.edit("brute.cpp", "++pairs;", "pairs += 2;")
        errs = self.run_check()["errors"]
        self.assertTrue(any(e.startswith("gate 2") for e in errs), errs)
        self.assertFalse(any(e.startswith("gate 1") for e in errs), errs)

    def test_brute_force_that_crashes_on_fuzz(self):
        self.edit("brute.cpp", "long long pairs = 0;", "long long pairs = 0; if (a.size() == 5) { volatile int* p = nullptr; *p = 1; }")
        errs = self.run_check()["errors"]
        self.assertTrue(any("fuzz input" in e and "RE" in e for e in errs), errs)

    def test_format_errors_are_reported_without_compiling(self):
        os.remove(os.path.join(self.dir, "driver.cpp"))
        errs = self.run_check()["errors"]
        self.assertEqual(len(errs), 1)
        self.assertTrue(errs[0].startswith("format:") and "driver.cpp" in errs[0], errs)

    def test_errors_are_capped(self):
        self.edit("brute.cpp", "++pairs;", "pairs += 2;")
        self.assertLessEqual(len(self.run_check()["errors"]), build.MAX_ERRORS)

    def test_cli_exit_codes_and_filter(self):
        script = os.path.join(HERE, "build.py")
        ok = subprocess.run([sys.executable, script, "--check", "--root", self.root, "pair-sum"], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertIn("1 of 1 problems pass", ok.stdout)
        unknown = subprocess.run([sys.executable, script, "--check", "--root", self.root, "nope"], capture_output=True, text=True)
        self.assertEqual(unknown.returncode, 1)
        self.edit("solution.cpp", "pairs += it->second;", "pairs += it->second + 1;")
        bad = subprocess.run([sys.executable, script, "--check", "--root", self.root], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("FAIL", bad.stdout)


    def set_enforce(self, enforce):
        path = os.path.join(self.dir, "problem.json")
        with open(path) as f:
            data = json.load(f)
        data["enforce"] = enforce
        with open(path, "w") as f:
            json.dump(data, f)

    # ---- gate 3
    def test_fast_brute_force_fails_gate_3(self):
        shutil.copy(os.path.join(self.dir, "solution.cpp"), os.path.join(self.dir, "brute.cpp"))
        errs = self.run_check()["errors"]
        self.assertTrue(any(e.startswith("gate 3") and "do not enforce" in e and "(time)" in e for e in errs), errs)

    def test_space_enforced_needs_a_brute_force_that_hits_mle(self):
        self.set_enforce({"time": False, "time_reason": "not tested here", "space": True})
        errs = self.run_check()["errors"]
        self.assertTrue(any("(space)" in e and "MLE" in e for e in errs), errs)

    def test_space_enforced_passes_when_the_brute_force_exceeds_memory(self):
        self.set_enforce({"time": False, "time_reason": "not tested here", "space": True})
        self.edit("brute.cpp", "#include <vector>", "#include <cstdlib>\n#include <vector>")
        self.edit("brute.cpp", "long long pairs = 0;",
                  "long long pairs = 0; if (a.size() > 100000) { volatile char* big = (volatile char*)malloc(400u << 20); "
                  "for (size_t i = 0; i < (400u << 20); i += 4096) big[i] = 1; }")
        r = self.run_check()
        self.assertEqual(r["errors"], [])
        self.assertIn("brute MLE", r["info"])

    def test_dimension_not_enforced_is_reported_and_needs_no_hit(self):
        self.set_enforce({"time": False, "time_reason": "fixture", "space": False, "space_reason": "fixture"})
        shutil.copy(os.path.join(self.dir, "solution.cpp"), os.path.join(self.dir, "brute.cpp"))
        r = self.run_check()
        self.assertEqual(r["errors"], [])
        self.assertIn("time not enforced", r["info"])

    def test_reference_headroom_check(self):
        scale = [{"name": "big", "wall_ms": 600.0, "peak_mb": 200.0}]
        self.assertEqual(build.reference_headroom_errors(scale, 1000, 256, {"time": False, "space": False}), [])
        self.assertEqual(len(build.reference_headroom_errors(scale, 1000, 256, {"time": True, "space": True})), 2)
        ok = [{"name": "big", "wall_ms": 400.0, "peak_mb": 100.0}]
        self.assertEqual(build.reference_headroom_errors(ok, 1000, 256, {"time": True, "space": True}), [])

    # ---- site output
    def build_main(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = build.main(list(args))
        return code, buf.getvalue()

    def test_check_mode_writes_nothing(self):
        out = os.path.join(self.root, "out")
        code, _ = self.build_main("--check", "--root", self.root, "--out", out)
        self.assertEqual(code, 0)
        self.assertFalse(os.path.exists(out))

    def test_build_writes_pages_and_index(self):
        out = os.path.join(self.root, "out")
        code, text = self.build_main("--root", self.root, "--out", out)
        self.assertEqual(code, 0, text)
        with open(os.path.join(out, "problems", "pair-sum", "index.html")) as f:
            self.assertIn("Pair Sum Count", f.read())
        with open(os.path.join(out, "data", "problems.json")) as f:
            self.assertEqual([x["id"] for x in json.load(f)["problems"]], ["pair-sum"])

    def test_failing_problem_writes_no_site(self):
        self.edit("solution.cpp", "pairs += it->second;", "pairs += it->second + 1;")
        out = os.path.join(self.root, "out")
        code, _ = self.build_main("--root", self.root, "--out", out)
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(out))


if __name__ == "__main__":
    unittest.main()
