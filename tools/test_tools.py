"""Unit tests for tools/gens.py, tools/problem.py and the fixture problem.

  python3 -m unittest discover -s tools -p "test_*.py"
"""
import copy
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gens  # noqa: E402
import problem  # noqa: E402
import runner  # noqa: E402

FIXTURE = os.path.join(HERE, "fixtures", "pair-sum")


class GensTests(unittest.TestCase):
    def test_same_spec_same_output(self):
        spec = {"gen": "array", "seed": 3, "n": 50, "lo": 0, "hi": 9, "k": 4}
        self.assertEqual(gens.generate(spec), gens.generate(spec))

    def test_different_seed_differs(self):
        a = gens.generate({"gen": "array", "seed": 1, "n": 40, "lo": 0, "hi": 1000})
        b = gens.generate({"gen": "array", "seed": 2, "n": 40, "lo": 0, "hi": 1000})
        self.assertNotEqual(a, b)

    def test_array_shape_and_k_header(self):
        lines = gens.generate({"gen": "array", "seed": 1, "n": 7, "lo": -3, "hi": 3, "k": 2}).split("\n")
        self.assertEqual(lines[0], "7 2")
        vals = list(map(int, lines[1].split()))
        self.assertEqual(len(vals), 7)
        self.assertTrue(all(-3 <= v <= 3 for v in vals))

    def test_array_distinct_and_sorted(self):
        vals = list(map(int, gens.generate({"gen": "array", "seed": 5, "n": 20, "lo": 0, "hi": 40, "distinct": True,
                                            "sorted": True}).split("\n")[1].split()))
        self.assertEqual(vals, sorted(set(vals)))
        self.assertEqual(len(vals), 20)

    def test_ranged_parameter_is_drawn_inside_range(self):
        sizes = {int(gens.generate({"gen": "array", "seed": s, "n": [2, 5]}).split("\n")[0]) for s in range(40)}
        self.assertTrue(sizes <= {2, 3, 4, 5} and len(sizes) > 1)

    def test_grid_shape(self):
        out = gens.generate({"gen": "grid", "seed": 1, "rows": 4, "cols": 6}).strip().split("\n")
        self.assertEqual(out[0], "4 6")
        self.assertEqual(len(out) - 1, 4)
        self.assertTrue(all(len(r.split()) == 6 for r in out[1:]))

    def test_graph_connected_has_no_duplicate_edges(self):
        out = gens.generate({"gen": "graph", "seed": 4, "n": 12, "m": 20, "connected": True}).strip().split("\n")
        n, m = map(int, out[0].split())
        edges = [tuple(sorted(map(int, l.split()[:2]))) for l in out[1:]]
        self.assertEqual((n, len(edges)), (12, m))
        self.assertEqual(len(set(edges)), len(edges))
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for u, v in edges:
            parent[find(u)] = find(v)
        self.assertEqual(len({find(i) for i in range(n)}), 1)

    def test_snake_grid_is_a_single_corridor(self):
        out = gens.generate({"gen": "snake_grid", "rows": 5, "cols": 5}).strip().split("\n")
        self.assertEqual(out[0], "5 5")
        grid = [list(map(int, r.split())) for r in out[1:]]
        self.assertEqual(grid[0][0], 2)
        self.assertEqual(sum(v == 2 for row in grid for v in row), 1)
        # breadth-first rot: every fresh cell is reached and the last one rots at minute 16
        seen, frontier, minutes = {(0, 0)}, [(0, 0)], 0
        while frontier:
            nxt = []
            for r, c in frontier:
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < 5 and 0 <= cc < 5 and grid[rr][cc] == 1 and (rr, cc) not in seen:
                        seen.add((rr, cc))
                        nxt.append((rr, cc))
            if nxt:
                minutes += 1
            frontier = nxt
        self.assertEqual(minutes, 16)
        self.assertEqual(len(seen), sum(v != 0 for row in grid for v in row))

    def test_permutation_is_a_permutation(self):
        out = gens.generate({"gen": "permutation", "seed": 2, "n": 30}).strip().split("\n")
        self.assertEqual(sorted(map(int, out[1].split())), list(range(1, 31)))

    def test_string_alphabet(self):
        s = gens.generate({"gen": "string", "seed": 1, "n": 100, "alphabet": "ab"}).strip()
        self.assertEqual(len(s), 100)
        self.assertTrue(set(s) <= {"a", "b"})

    def test_unknown_generator_rejected(self):
        with self.assertRaises(ValueError):
            gens.generate({"gen": "nope"})

    def test_fuzz_inputs_count_and_variety(self):
        outs = gens.fuzz_inputs({"runs": 25, "seed": 10, "spec": {"gen": "array", "n": [1, 8], "lo": 0, "hi": 9}})
        self.assertEqual(len(outs), 25)
        self.assertGreater(len(set(outs)), 10)


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="dojo-test-")
        self.dir = os.path.join(self.tmp, "pair-sum")
        shutil.copytree(FIXTURE, self.dir)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def mutate(self, fn, name="problem.json"):
        path = os.path.join(self.dir, name)
        with open(path) as f:
            data = json.load(f)
        fn(data)
        with open(path, "w") as f:
            json.dump(data, f)

    def errors(self):
        return problem.validate(self.dir)

    def test_fixture_is_valid(self):
        self.assertEqual(problem.validate(FIXTURE), [])

    def test_missing_file(self):
        os.remove(os.path.join(self.dir, "brute.cpp"))
        self.assertTrue(any("brute.cpp" in e for e in self.errors()))

    def test_id_must_match_folder(self):
        self.mutate(lambda d: d.update(id="other"))
        self.assertTrue(any("folder name" in e for e in self.errors()))

    def test_quiz_needs_four_distinct_options(self):
        self.mutate(lambda d: d["quiz"][0].update(options=["a", "b", "c"]))
        self.assertTrue(any("4 distinct" in e for e in self.errors()))
        self.mutate(lambda d: d["quiz"][0].update(options=["a", "a", "b", "c"]))
        self.assertTrue(any("4 distinct" in e for e in self.errors()))

    def test_quiz_needs_complexity_questions(self):
        self.mutate(lambda d: d["quiz"][1].update(tag="Other"))
        self.assertTrue(any("Space complexity" in e for e in self.errors()))

    def test_quiz_answer_range(self):
        self.mutate(lambda d: d["quiz"][0].update(answer=4))
        self.assertTrue(any("answer" in e for e in self.errors()))

    def test_unenforced_dimension_needs_reason(self):
        self.mutate(lambda d: d["enforce"].pop("space_reason"))
        self.assertTrue(any("space_reason" in e for e in self.errors()))

    def test_enforced_dimension_needs_scale_test(self):
        self.mutate(lambda t: t.update(scale=[]), "tests.json")
        self.assertTrue(any("scale test" in e for e in self.errors()))

    def test_unknown_scale_generator(self):
        self.mutate(lambda t: t["scale"][0]["spec"].update(gen="bogus"), "tests.json")
        self.assertTrue(any("unknown generator" in e for e in self.errors()))

    def test_needs_hidden_and_visible_cases(self):
        def all_visible(t):
            for c in t["cases"]:
                c["visible"] = True
        self.mutate(all_visible, "tests.json")
        self.assertTrue(any("hidden" in e for e in self.errors()))

    def test_duplicate_case_names(self):
        self.mutate(lambda t: t["cases"][1].update(name=t["cases"][0]["name"]), "tests.json")
        self.assertTrue(any("unique" in e for e in self.errors()))

    def test_fuzz_required(self):
        self.mutate(lambda t: t.pop("fuzz"), "tests.json")
        self.assertTrue(any("fuzz" in e for e in self.errors()))

    def test_bad_clarification_regex(self):
        self.mutate(lambda d: d["interview"]["clarifications"][0].update(match="("))
        self.assertTrue(any("regex" in e for e in self.errors()))

    def test_nudges_exactly_two(self):
        self.mutate(lambda d: d["interview"]["nudges"].append("one more"))
        self.assertTrue(any("nudges" in e for e in self.errors()))


class FixtureProgramsTests(unittest.TestCase):
    """The fixture's reference and brute force must agree, and the brute force must be the slow one."""

    @classmethod
    def setUpClass(cls):
        cls.ctx = runner.workdir()
        cls.dir = cls.ctx.__enter__()
        cls.exes = {}
        for name in ("solution", "brute"):
            work = os.path.join(cls.dir, name)
            os.makedirs(work)
            shutil.copy(os.path.join(FIXTURE, "driver.cpp"), work)
            shutil.copy(os.path.join(FIXTURE, name + ".cpp"), os.path.join(work, "solution.cpp"))
            exe = os.path.join(work, "run")
            ok, msg = runner.compile_cpp([os.path.join(work, "driver.cpp")], exe, include_dirs=[work])
            if not ok:
                raise RuntimeError(name + " did not compile: " + msg)
            cls.exes[name] = exe

    @classmethod
    def tearDownClass(cls):
        cls.ctx.__exit__(None, None, None)

    def test_hand_cases_pass_for_both(self):
        _, tests = problem.load(FIXTURE)
        for case in tests["cases"]:
            for name, exe in self.exes.items():
                r = runner.run_exe(exe, case["input"])
                self.assertEqual(r["status"], "OK", (name, case["name"]))
                self.assertTrue(runner.same_output(case["expected"], r["stdout"]), (name, case["name"], r["stdout"]))

    def test_fuzz_agreement(self):
        _, tests = problem.load(FIXTURE)
        for text in gens.fuzz_inputs(tests["fuzz"]):
            a = runner.run_exe(self.exes["solution"], text)
            b = runner.run_exe(self.exes["brute"], text)
            self.assertTrue(runner.same_output(a["stdout"], b["stdout"]), text)

    def test_scale_separates_reference_from_brute(self):
        _, tests = problem.load(FIXTURE)
        text = gens.generate(tests["scale"][0]["spec"])
        ref = runner.run_exe(self.exes["solution"], text, time_limit_ms=1000)
        brute = runner.run_exe(self.exes["brute"], text, time_limit_ms=1000)
        self.assertEqual(ref["status"], "OK")
        self.assertLess(ref["wall_ms"], 500)
        self.assertEqual(brute["status"], "TLE")


if __name__ == "__main__":
    unittest.main()
