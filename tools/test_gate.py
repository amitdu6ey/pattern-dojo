"""Tests for tools/gate.py. It runs fake steps, never the real gate (that would recurse).

  python3 -m unittest discover -s tools -p "test_*.py"
"""
import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate  # noqa: E402

PY = sys.executable


def run_quietly(steps):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = gate.run(steps)
    return code, buf.getvalue()


class GateTests(unittest.TestCase):
    def test_all_steps_pass(self):
        code, out = run_quietly([("a", [PY, "-c", "pass"]), ("b", [PY, "-c", "pass"])])
        self.assertEqual(code, 0)
        self.assertIn("gate passed", out)

    def test_failure_stops_the_gate_and_returns_non_zero(self):
        code, out = run_quietly([("good", [PY, "-c", "pass"]), ("bad", [PY, "-c", "import sys; sys.exit(3)"]),
                                 ("never", [PY, "-c", "print('should not run')"])])
        self.assertEqual(code, 1)
        self.assertIn("gate FAILED at: bad", out)
        self.assertNotIn("never", out.replace("gate FAILED at: bad", ""))

    def test_failure_output_is_shown(self):
        code, out = run_quietly([("noisy", [PY, "-c", "import sys; print('boom detail'); sys.exit(1)"])])
        self.assertEqual(code, 1)
        self.assertIn("boom detail", out)

    def test_real_steps_are_defined_and_exist(self):
        names = [n for n, _ in gate.STEPS]
        self.assertEqual(names[0], "unit tests")
        self.assertIn("site build", names)
        for _, cmd in gate.STEPS:
            scripts = [c for c in cmd if c.startswith("tools/") and c.endswith(".py")]
            for s in scripts:
                self.assertTrue(os.path.isfile(os.path.join(gate.ROOT, s)), s)


if __name__ == "__main__":
    unittest.main()
