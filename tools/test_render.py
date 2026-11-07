"""Tests for tools/render.py, web/patterns.json, web/theme.css and the generated site.

  python3 -m unittest discover -s tools -p "test_*.py"
"""
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build  # noqa: E402
import problem  # noqa: E402
import render  # noqa: E402

FIXTURE = os.path.join(HERE, "fixtures", "pair-sum")


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for key in ("href", "src"):
            if d.get(key):
                self.refs.append(d[key])


def local_refs(html_text):
    p = _Links()
    p.feed(html_text)
    return [r for r in p.refs if not re.match(r"^(https?:|mailto:|#)", r)]


class RenderTests(unittest.TestCase):
    def test_page_links_theme_relative_to_depth(self):
        for depth, prefix in ((0, ""), (1, "../"), (2, "../../")):
            out = render.page("T", "<p>x</p>", depth=depth)
            self.assertIn('href="%sassets/theme.css"' % prefix, out)
            self.assertIn('href="%sindex.html"' % prefix, out)

    def test_title_is_escaped(self):
        self.assertIn("<title>A &lt;b&gt; &amp; c</title>", render.page("A <b> & c", ""))

    def test_pages_state_they_are_read_only(self):
        self.assertIn("Read-only site", render.page("T", ""))

    def test_patterns_file_is_valid(self):
        pats = render.load_patterns()
        ids = [p["id"] for p in pats]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", i) for i in ids))
        self.assertTrue(all(p["name"].strip() for p in pats))
        self.assertEqual(problem.known_patterns(), ids)

    def test_theme_defines_tokens_before_dark_overrides(self):
        with open(os.path.join(ROOT, "web", "theme.css")) as f:
            css = f.read()
        first_root = css.index(":root {")
        self.assertLess(first_root, css.index("prefers-color-scheme: dark"))
        self.assertLess(first_root, css.index(':root[data-theme="dark"]'))
        self.assertIn('[data-theme="light"]', css)
        self.assertRegex(css, r"body \{[^}]*background: var\(--bg\)")

    def test_home_lists_every_pattern_with_counts(self):
        pats = render.load_patterns()
        out = render.home_page(pats, [{"pattern": "arrays-and-hashing"}])
        for p in pats:
            self.assertIn(p["name"], out)
        self.assertIn("1 problem<", out)
        self.assertIn("0 problems", out)
        self.assertNotIn("Under construction", out)
        self.assertIn("Under construction", render.home_page(pats, []))


class ProblemPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p, _ = problem.load(FIXTURE)
        cls.out = render.problem_page(cls.p, "Arrays and hashing")

    def test_split_view_structure(self):
        for needle in ('class="split"', 'class="pane left"', 'class="pane right"', 'id="editor"', 'class="wrap wide"'):
            self.assertIn(needle, self.out)

    def test_statement_examples_and_constraints_are_shown(self):
        self.assertIn("count the pairs of positions", self.out.replace("Count", "count"))
        self.assertIn("1 5 3 3 2", self.out)
        self.assertIn("1 &lt;= n &lt;= 200000", self.out)

    def test_hints_start_hidden_and_a_button_reveals_them(self):
        self.assertEqual(self.out.count('class="hint" hidden'), len(self.p["hints"]))
        self.assertIn("Show hint 1 of %d" % len(self.p["hints"]), self.out)

    def test_explanation_is_in_the_page_but_hidden(self):
        self.assertIn('<section id="after" hidden>', self.out)
        for text in (self.p["idea"], self.p["naive"], self.p["complexity"]["time_why"], self.p["mistakes"][0]):
            self.assertIn(render.esc(text), self.out)
        self.assertLess(self.out.index('id="hints"'), self.out.index('<section id="after" hidden>'))

    def test_run_and_submit_are_disabled_until_the_judge_exists(self):
        self.assertEqual(self.out.count("disabled>"), 2)
        self.assertIn("local judge", self.out)

    def test_starter_code_is_escaped(self):
        self.assertIn("#include &lt;vector&gt;", self.out)
        self.assertNotIn("#include <vector>", self.out)

    def test_scripts_are_linked_relative_to_depth_2(self):
        self.assertIn('src="../../assets/progress.js"', self.out)
        self.assertIn('src="../../assets/problem.js"', self.out)
        self.assertLess(self.out.index("progress.js"), self.out.index("problem.js"))

    def test_untrusted_text_is_escaped(self):
        evil = dict(self.p, title="<script>alert(1)</script>", statement="a <b>bold</b> claim")
        out = render.problem_page(evil, "<i>x</i>")
        self.assertNotIn("<script>alert(1)</script>", out)
        self.assertNotIn("<b>bold</b>", out)
        self.assertNotIn("<i>x</i>", out)

    def test_every_element_id_used_by_problem_js_exists_in_the_page(self):
        with open(os.path.join(ROOT, "web", "problem.js")) as f:
            ids = set(re.findall(r'getElementById\("([^"]+)"\)', f.read()))
        self.assertTrue({"problem", "moreHint", "after", "giveUp", "giveUpAsk", "giveUpYes", "giveUpNo", "editor"} <= ids)
        for i in ids:
            self.assertIn('id="%s"' % i, self.out, "problem.js uses #%s but the page has no such element" % i)

    def test_progress_js_exposes_the_api_problem_js_uses(self):
        with open(os.path.join(ROOT, "web", "progress.js")) as f:
            src = f.read()
        with open(os.path.join(ROOT, "web", "problem.js")) as f:
            used = set(re.findall(r"P\.(\w+)\(", f.read()))
        for name in used:
            self.assertRegex(src, r"\b%s:\s*function" % name, "progress.js has no %s" % name)


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="dojo-site-")
        shutil.copytree(FIXTURE, os.path.join(cls.root, "problems", "pair-sum"))
        cls.out = os.path.join(cls.root, "site")
        build.write_site([os.path.join(cls.root, "problems", "pair-sum")], cls.out)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def read(self, rel):
        with open(os.path.join(self.out, rel), encoding="utf-8") as f:
            return f.read()

    def test_expected_files_exist(self):
        for rel in ("index.html", "assets/theme.css", "assets/progress.js", "assets/problem.js", "data/problems.json", "problems/pair-sum/index.html",
                    "patterns/arrays-and-hashing/index.html", "patterns/graphs/index.html"):
            self.assertTrue(os.path.isfile(os.path.join(self.out, rel)), rel)

    def test_every_pattern_has_a_page(self):
        for p in render.load_patterns():
            self.assertTrue(os.path.isfile(os.path.join(self.out, "patterns", p["id"], "index.html")), p["id"])

    def test_every_local_link_resolves(self):
        checked = 0
        for dirpath, _, files in os.walk(self.out):
            for name in files:
                if not name.endswith(".html"):
                    continue
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8") as f:
                    for ref in local_refs(f.read()):
                        target = os.path.normpath(os.path.join(dirpath, ref.split("#")[0]))
                        self.assertTrue(os.path.exists(target), "%s links to missing %s" % (path, ref))
                        checked += 1
        self.assertGreater(checked, 50)

    def test_pattern_page_lists_the_problem_and_empty_pattern_says_so(self):
        self.assertIn("Pair Sum Count", self.read("patterns/arrays-and-hashing/index.html"))
        self.assertIn("No problems yet", self.read("patterns/graphs/index.html"))

    def test_problem_page_links_back_to_its_pattern(self):
        text = self.read("problems/pair-sum/index.html")
        self.assertIn('href="../../patterns/arrays-and-hashing/index.html"', text)
        self.assertIn("Arrays and hashing", text)

    def test_index_json(self):
        data = json.loads(self.read("data/problems.json"))
        self.assertEqual([p["id"] for p in data["problems"]], ["pair-sum"])

    def test_unknown_pattern_fails_validation(self):
        d = os.path.join(self.root, "bad")
        shutil.copytree(FIXTURE, d)
        path = os.path.join(d, "problem.json")
        with open(path) as f:
            data = json.load(f)
        data["id"] = "bad"
        data["pattern"] = "not-a-pattern"
        with open(path, "w") as f:
            json.dump(data, f)
        self.assertTrue(any("web/patterns.json" in e for e in problem.validate(d)))


if __name__ == "__main__":
    unittest.main()
