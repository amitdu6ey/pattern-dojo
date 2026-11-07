"""HTML for the site: one shared layout and the pages built from it. Standard library only.

Links are relative, so the site works from any folder (GitHub Pages serves it under /pattern-dojo/).
`depth` is how many folders below the site root the page lives.
"""
import html
import json
import os

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


def page(title, body, depth=0, wide=False, current="Problems"):
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
        "<p>%s</p></footer>\n</div>\n</body>\n</html>\n"
    ) % (esc(title), FONTS, root, " wide" if wide else "", root, nav, body, docs)


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


def problem_page(p, pattern_name):
    """A stub problem page. The real template arrives with P0.3."""
    body = ('<p><a class="crumb" href="../../patterns/%s/index.html">← %s</a></p>\n<h1>%s</h1>\n'
            '<p class="tags">%s · %s · %s</p>\n<p>%s</p>\n'
            '<p class="note">The full problem page arrives with the page template (P0.3).</p>'
            % (esc(p["pattern"]), esc(pattern_name), esc(p["title"]), esc(pattern_name), esc(p["difficulty"]),
               esc(p["level"]), esc(p["statement"])))
    return page(p["title"], body, depth=2)
