"""HTML for the site: one shared layout and the pages built from it. Standard library only.

Links are relative, so the site works from any folder (GitHub Pages serves it under /pattern-dojo/).
`depth` is how many folders below the site root the page lives.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_BLOB = "https://github.com/amitdu6ey/pattern-dojo/blob/main/"
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&'
         'family=Schibsted+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">')
DOCS = [("Roadmap", "ROADMAP.md"), ("Learning strategy", "LEARNING.md"), ("Research", "RESEARCH.md"), ("Log", "LOG.md")]


def esc(text):
    return html.escape(str(text), quote=True)


def load_patterns():
    with open(os.path.join(ROOT, "web", "patterns.json"), encoding="utf-8") as f:
        return json.load(f)["patterns"]


def page(title, body, depth=0, wide=False, current="Problems", scripts=()):
    """A full HTML page with the shared header, theme and footer."""
    root = "../" * depth
    nav = '<a href="%sindex.html"%s>Problems</a>' % (root, ' aria-current="page"' if current == "Problems" else "")
    docs = "".join('<a href="%s%s">%s</a>' % (REPO_BLOB, f, esc(n)) for n, f in DOCS)
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n%s\n"
        '<link rel="stylesheet" href="%sassets/theme.css">\n</head>\n<body>\n'
        '<div class="wrap%s">\n'
        '<header class="top"><a class="brand" href="%sindex.html">Pattern Dojo</a><nav aria-label="Main">%s</nav></header>\n'
        "<main>\n%s\n</main>\n"
        '<footer><p>Read-only site. Running and submitting code needs the local judge, which you start on your own machine.</p>'
        "<p>%s</p></footer>\n</div>\n%s</body>\n</html>\n"
    ) % (esc(title), FONTS, root, " wide" if wide else "", root, nav, body, docs,
         "".join('<script src="%sassets/%s"></script>\n' % (root, s) for s in scripts))


def home_page(patterns, problems):
    """Home: the list of patterns with how many problems each has."""
    by_pattern = {}
    for p in problems:
        by_pattern.setdefault(p["pattern"], []).append(p)
    rows = []
    for pat in patterns:
        n = len(by_pattern.get(pat["id"], []))
        rows.append('<li><a href="patterns/%s/index.html">%s</a><span class="meta">%d problem%s</span></li>'
                    % (esc(pat["id"]), esc(pat["name"]), n, "" if n == 1 else "s"))
    intro = ""
    if not problems:
        intro = '<p class="muted">Under construction. Problems appear here as they are built and tested.</p>'
    body = ('<section><h2>Patterns</h2>\n%s<ul class="rows">\n%s\n</ul></section>' % (intro, "\n".join(rows)))
    return page("Pattern Dojo", body, depth=0)


def pattern_page(pattern, problems):
    """One pattern: a plain list of its problems."""
    rows = "\n".join(
        '<li><a href="../../problems/%s/index.html">%s</a><span class="meta">%s · %s</span></li>'
        % (esc(p["id"]), esc(p["title"]), esc(p["difficulty"]), esc(p["level"])) for p in problems)
    if not rows:
        rows = '<li><span class="muted">No problems yet.</span></li>'
    body = ('<p><a class="crumb" href="../../index.html">← Patterns</a></p>\n<h1>%s</h1>\n'
            '<section><h2>Problems</h2><ul class="rows">\n%s\n</ul></section>' % (esc(pattern["name"]), rows))
    return page(pattern["name"], body, depth=2)


_CPP_TOKEN = re.compile(
    r"(?P<cm>//.*$)|(?P<pp>^\s*#.*$)"
    r"|\b(?P<kw>int|long|short|char|bool|double|float|void|auto|const|static|unsigned|signed|for|while|do|if|else|"
    r"continue|break|return|struct|class|using|namespace|true|false|nullptr|new|delete|template|typename)\b"
    r"|\b(?P<ty>vector|queue|pair|unordered_map|unordered_set|map|set|string|stack|deque|priority_queue|array|"
    r"size_t|tuple)\b"
    r"|\b(?P<num>\d+)\b")


def highlight_cpp(line):
    """HTML for one line of C++ with a few token classes. Only the pieces between tokens and the tokens are escaped."""
    out, last = [], 0
    for m in _CPP_TOKEN.finditer(line):
        out.append(esc(line[last:m.start()]))
        out.append('<span class="%s">%s</span>' % (m.lastgroup, esc(m.group(0))))
        last = m.end()
    out.append(esc(line[last:]))
    return "".join(out)


def walkthrough_html(steps, code):
    """The annotated solution: step tabs, the explanation of each step, and the numbered code. problem.js wires it up."""
    lines = code.splitlines()
    tabs = "".join('<button type="button" class="wt-tab" data-step="%d" aria-pressed="false">%s</button>' % (i, esc(s["tab"]))
                   for i, s in enumerate(steps))
    texts = "".join('<p class="wt-text" data-step="%d" data-first="%d" data-last="%d" hidden><span class="where">%s</span>%s</p>'
                    % (i, s["lines"][0], s["lines"][1],
                       "Line %d" % s["lines"][0] if s["lines"][0] == s["lines"][1]
                       else "Lines %d to %d" % tuple(s["lines"]), esc(s["text"]))
                    for i, s in enumerate(steps))
    code_html = "".join('<div class="ln" data-n="%d"><span class="no">%d</span><span class="src">%s</span></div>'
                        % (i + 1, i + 1, highlight_cpp(l)) for i, l in enumerate(lines))
    return ('<h2>Solution walkthrough</h2>\n<div class="steps" id="wtTabs" role="group" aria-label="Walkthrough steps">%s</div>\n'
            '<div class="wt-texts">%s</div>\n<div class="codeview" role="region" aria-label="Reference solution in C++">%s</div>\n'
            % (tabs, texts, code_html))


def problem_page(p, pattern_name, solution_code=""):
    """The problem page: a split view with the problem on the left and the editor on the right.

    The explanation (idea, complexity, mistakes) is in the page but hidden. web/problem.js shows it once the learner
    has solved the problem or given up. Run and Submit arrive with the local judge (P0.4 and P0.5).
    """
    tags = " · ".join([pattern_name] + list(p.get("tags") or []) + [p["difficulty"].capitalize()])
    examples = "".join(
        '<pre>%s\n→ %s</pre><p class="muted">%s</p>' % (esc(e["input"]), esc(e["output"]), esc(e["explain"]))
        for e in p["examples"])
    constraints = "".join("<li>%s</li>" % esc(c) for c in p["constraints"])
    hints = "".join('<div class="hint" hidden><span class="muted mono">%d</span> %s</div>' % (i + 1, esc(h))
                    for i, h in enumerate(p["hints"]))
    mistakes = "".join("<li>%s</li>" % esc(m) for m in p["mistakes"])
    c = p["complexity"]
    walkthrough = walkthrough_html(p["walkthrough"], solution_code) if p.get("walkthrough") and solution_code else ""
    left = (
        '<p><a class="crumb" href="../../patterns/%s/index.html">← %s</a></p>\n'
        '<h1 style="margin-top:0.8rem">%s</h1>\n<p class="tags">%s</p>\n'
        "<p>%s</p>\n"
        '<p class="muted">Input: %s<br>Output: %s</p>\n'
        "<h2>Examples</h2>\n%s\n"
        "<h2>Constraints</h2>\n<ul class=\"plain\">%s</ul>\n"
        '<h2>Hints</h2>\n<div id="hints">%s</div>\n'
        '<p><button class="link" id="moreHint" type="button">Show hint 1 of %d</button></p>\n'
        '<section id="after" hidden>\n'
        "<h2>The idea</h2>\n<p>%s</p>\n"
        "<h2>Why the naive approach is slow</h2>\n<p>%s</p>\n"
        "<h2>Complexity</h2>\n"
        "<p><span class=\"mono\">Time %s.</span> %s</p>\n<p><span class=\"mono\">Space %s.</span> %s</p>\n"
        "<h2>Common mistakes</h2>\n<ul class=\"plain\">%s</ul>\n"
        "%s</section>\n"
        '<p class="note"><button class="link" id="giveUp" type="button">Give up and show the explanation</button>'
        '<span id="giveUpAsk" hidden>Show it now? This counts as not solved. '
        '<button class="link" id="giveUpYes" type="button">Yes, show it</button> '
        '<button class="link" id="giveUpNo" type="button">No, keep going</button></span></p>'
    ) % (esc(p["pattern"]), esc(pattern_name), esc(p["title"]), esc(tags), esc(p["statement"]),
         esc(p["input_format"]), esc(p["output_format"]), examples, constraints, hints, len(p["hints"]),
         esc(p["idea"]), esc(p["naive"]), esc(c["time"]), esc(c["time_why"]), esc(c["space"]), esc(c["space_why"]),
         mistakes, walkthrough)
    right = (
        '<div class="rowbar"><span class="mono">C++</span><span>Starter code</span></div>\n'
        '<textarea class="code" id="editor" spellcheck="false" aria-label="C++ solution">%s</textarea>\n'
        '<div class="actions"><button class="btn" type="button" disabled>Run</button>'
        '<button class="btn primary" type="button" disabled>Submit</button>'
        '<span class="muted" style="font-size:0.85rem">Running and submitting arrive with the local judge.</span></div>'
    ) % esc(p["starter"])
    body = ('<div id="problem" data-problem-id="%s" class="split"><div class="pane left">%s</div>'
            '<div class="pane right">%s</div></div>' % (esc(p["id"]), left, right))
    return page(p["title"], body, depth=2, wide=True, scripts=("progress.js", "problem.js"))
