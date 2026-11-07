#!/usr/bin/env python3
"""Load and validate a problem folder (the format is described in tools/FORMAT.md).

  python3 tools/problem.py problems/001-rotting-oranges     # validate one
  python3 tools/problem.py                                  # validate every folder in problems/
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gens  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERNS_FILE = os.path.join(ROOT, "web", "patterns.json")
FILES = ("problem.json", "tests.json", "solution.cpp", "driver.cpp", "brute.cpp")
DIFFICULTIES = {"easy", "medium", "hard"}
LEVELS = {"basic", "variant", "combined"}


def known_patterns():
    with open(PATTERNS_FILE, encoding="utf-8") as f:
        return [x["id"] for x in json.load(f)["patterns"]]


def load(path):
    """Return (problem, tests) parsed from a problem folder."""
    with open(os.path.join(path, "problem.json"), encoding="utf-8") as f:
        problem = json.load(f)
    with open(os.path.join(path, "tests.json"), encoding="utf-8") as f:
        tests = json.load(f)
    return problem, tests


def problem_dirs(root=None):
    base = root or os.path.join(ROOT, "problems")
    if not os.path.isdir(base):
        return []
    return sorted(os.path.join(base, d) for d in os.listdir(base) if os.path.isfile(os.path.join(base, d, "problem.json")))


def _text(v):
    return isinstance(v, str) and v.strip() != ""


def _strings(v, at_least=0):
    return isinstance(v, list) and len(v) >= at_least and all(_text(x) for x in v)


def validate(path):
    """Return a list of error strings. An empty list means the folder is valid."""
    errs = []
    for name in FILES:
        if not os.path.isfile(os.path.join(path, name)):
            errs.append("missing file: " + name)
    if errs:
        return errs
    try:
        p, t = load(path)
    except ValueError as e:
        return ["invalid JSON: %s" % e]

    def need(cond, msg):
        if not cond:
            errs.append(msg)

    need(p.get("id") == os.path.basename(os.path.normpath(path)), "id must equal the folder name")
    for k in ("title", "pattern", "statement", "input_format", "output_format", "idea", "naive", "starter"):
        need(_text(p.get(k)), "%s must be a non-empty string" % k)
    need(p.get("pattern") in known_patterns(), "pattern must be one of the ids in web/patterns.json")
    need(p.get("difficulty") in DIFFICULTIES, "difficulty must be one of %s" % sorted(DIFFICULTIES))
    need(p.get("level") in LEVELS, "level must be one of %s" % sorted(LEVELS))
    need(_strings(p.get("tags", []) or []), "tags must be a list of strings")
    need(_strings(p.get("concepts", []) or []), "concepts must be a list of strings")
    need(_strings(p.get("constraints"), 1), "constraints must be a non-empty list of strings")
    need(_strings(p.get("hints"), 3), "hints must have at least 3 strings")
    need(_strings(p.get("mistakes"), 2), "mistakes must have at least 2 strings")
    ex = p.get("examples")
    need(isinstance(ex, list) and len(ex) >= 1 and all(isinstance(e, dict) and _text(e.get("input")) and _text(e.get("output"))
                                                        and _text(e.get("explain")) for e in ex),
         "examples needs at least one item with input, output and explain")
    c = p.get("complexity")
    need(isinstance(c, dict) and all(_text(c.get(k)) for k in ("time", "time_why", "space", "space_why")),
         "complexity needs time, time_why, space and space_why")
    tl, ml = p.get("time_limit_ms"), p.get("memory_limit_mb")
    need(isinstance(tl, int) and 100 <= tl <= 10000, "time_limit_ms must be an integer from 100 to 10000")
    need(isinstance(ml, int) and 16 <= ml <= 1024, "memory_limit_mb must be an integer from 16 to 1024")

    enf = p.get("enforce")
    enforced = {}
    if not (isinstance(enf, dict) and isinstance(enf.get("time"), bool) and isinstance(enf.get("space"), bool)):
        errs.append("enforce needs boolean time and space")
    else:
        for dim in ("time", "space"):
            enforced[dim] = enf[dim]
            if not enf[dim]:
                need(_text(enf.get(dim + "_reason")), "enforce.%s is false, so enforce.%s_reason must explain why" % (dim, dim))

    quiz = p.get("quiz")
    if not (isinstance(quiz, list) and len(quiz) >= 4):
        errs.append("quiz needs at least 4 questions")
    else:
        tags = set()
        for i, q in enumerate(quiz):
            tag = "quiz[%d]" % i
            if not isinstance(q, dict):
                errs.append(tag + " must be an object")
                continue
            tags.add(q.get("tag"))
            need(_text(q.get("tag")) and _text(q.get("q")), tag + " needs tag and q")
            opts = q.get("options")
            need(isinstance(opts, list) and len(opts) == 4 and all(_text(o) for o in opts) and len(set(opts)) == 4,
                 tag + " needs exactly 4 distinct non-empty options")
            need(isinstance(q.get("answer"), int) and not isinstance(q.get("answer"), bool) and 0 <= q.get("answer") <= 3,
                 tag + " answer must be an integer from 0 to 3")
            need(_text(q.get("explanation")), tag + " needs an explanation")
        need("Time complexity" in tags and "Space complexity" in tags, "quiz needs Time complexity and Space complexity questions")

    iv = p.get("interview")
    if not isinstance(iv, dict):
        errs.append("interview must be an object")
    else:
        cl = iv.get("clarifications")
        ok = isinstance(cl, list) and len(cl) >= 3 and all(isinstance(x, dict) and _text(x.get("match")) and _text(x.get("answer")) for x in cl)
        need(ok, "interview.clarifications needs at least 3 items with match and answer")
        if ok:
            for x in cl:
                try:
                    re.compile(x["match"])
                except re.error as e:
                    errs.append("interview.clarifications match %r is not a valid regex: %s" % (x["match"], e))
        need(_strings(iv.get("nudges")) and len(iv.get("nudges") or []) == 2, "interview.nudges must be exactly 2 strings")
        fu = iv.get("followup")
        need(isinstance(fu, dict) and _text(fu.get("question")) and _text(fu.get("discussion")), "interview.followup needs question and discussion")
        need(_strings(iv.get("edge_cases"), 2), "interview.edge_cases needs at least 2 strings")

    # tests.json
    cases = t.get("cases")
    if not (isinstance(cases, list) and len(cases) >= 5):
        errs.append("tests: cases needs at least 5 items")
    else:
        names = [x.get("name") for x in cases if isinstance(x, dict)]
        need(len(names) == len(cases) and all(_text(n) for n in names) and len(set(names)) == len(names), "tests: case names must be unique non-empty strings")
        need(all(isinstance(x, dict) and isinstance(x.get("input"), str) and isinstance(x.get("expected"), str) for x in cases),
             "tests: every case needs string input and expected")
        vis = [x for x in cases if isinstance(x, dict) and x.get("visible") is True]
        need(len(vis) >= 2, "tests: at least 2 cases must be visible")
        need(len(cases) - len(vis) >= 1, "tests: at least 1 case must be hidden")
    scale = t.get("scale", [])
    need(isinstance(scale, list), "tests: scale must be a list")
    if isinstance(scale, list):
        for i, s in enumerate(scale):
            try:
                gens.check_spec(s.get("spec") if isinstance(s, dict) else None)
            except ValueError as e:
                errs.append("tests: scale[%d] %s" % (i, e))
            need(isinstance(s, dict) and _text(s.get("name")) and _text(s.get("label")), "tests: scale[%d] needs name and label" % i)
        if enforced.get("time") or enforced.get("space"):
            need(len(scale) >= 1, "tests: an enforced dimension needs at least one scale test")
    fz = t.get("fuzz")
    if not (isinstance(fz, dict) and isinstance(fz.get("runs"), int) and 20 <= fz["runs"] <= 500 and isinstance(fz.get("seed"), int)
            and isinstance(fz.get("spec"), dict)):
        errs.append("tests: fuzz needs runs (20 to 500), seed and spec")
    else:
        try:
            gens.generate(dict(fz["spec"], seed=fz["seed"]))
        except (ValueError, KeyError, TypeError) as e:
            errs.append("tests: fuzz spec does not generate: %s" % e)
    return errs


def main(argv):
    paths = argv or problem_dirs()
    if not paths:
        print("no problems found")
        return 0
    bad = 0
    for path in paths:
        errs = validate(path)
        print("%s %s" % ("ok  " if not errs else "FAIL", os.path.basename(os.path.normpath(path))))
        for e in errs:
            print("     - " + e)
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
