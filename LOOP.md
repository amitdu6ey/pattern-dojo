# Loop protocol

Read this first on every run. One run advances the platform by exactly one ROADMAP item.

## Steps
1. Read `state.json`.
   - `status` is `working` and `started_at` is less than 40 minutes ago: another run is in progress.
     Do nothing, say so in one line, and end the turn.
   - `status` is `working` and older than 40 minutes: the last run died. Add a line to `LOG.md`,
     set status to `idle`, and continue.
2. Take the first unchecked item in `ROADMAP.md`, top to bottom. If none are left, stop the loop and report.
3. Set `state.json` to `working` with `current` and `started_at` (`date -u +%FT%TZ`).
4. Do the item. One item per run. If it is too big for one run, split it into sub-items in `ROADMAP.md`,
   and do only the first.
5. Gate: once `tools/build.py` exists, `python3 tools/build.py --check` must pass before you commit.
   Never commit a failing build or a failing solution.
6. Tick the item in `ROADMAP.md`, append one line to `LOG.md` (date, item, what changed, how it was verified),
   set `state.json` to `idle` with `last_run`, then `git add -A` and `git commit -m "<item id>: <summary>"`.
7. Reply with two lines at most: what you did, and the next item.

## Hard rules
- Never run `git push`, publish an Artifact, create accounts, or enter credentials.
- The loop never fetches from LeetCode or any other site. Live fetching is a command the user runs. Build and
  test the fetcher against recorded fixtures that you write by hand and mark clearly as samples. Never present
  fixture data as real.
- Python is stdlib only (3.9). C++ is C++17 built with `g++`. No pip, no npm, no downloads.
  The static site may load Google Fonts and nothing else from the network.
- Do not spawn subagents. Keep chat output short; put detail in the repo.
- Temporary files go in the session scratchpad, not in the repo.

## Quality bar
- Problem statements are written in your own words. Never copy a platform's wording. Name the problem and
  link to it by title and number only.
- Every solution is C++17, uses explicit includes (no `bits/stdc++.h`), and is compiled and run by the build.
- Every problem has at least 5 test cases, including edge cases, plus a brute-force cross-check on small random
  inputs where that is feasible. A solution that has not run is not done.
- Every problem page covers: the idea in plain language, why the naive approach is slow, the pattern name,
  progressive hints, an annotated solution, complexity with the reason, and the common mistakes.
- The interface is minimal. This is a hard requirement from the user. One column, plain type, generous
  whitespace, and only the controls a screen needs. No hero banners, badges, stat tiles, decorative cards,
  gradients, icons-for-decoration, or animation beyond what teaches (the grid stepper is the exception). Prefer
  a list to a grid of cards, and a link to a button. Every element must earn its place; when unsure, leave it out.
  Reuse only the palette tokens and fonts from `seed/rotting-oranges.html`, not its panels and chrome.
- Light and dark themes, works at 400px wide, keyboard accessible, no horizontal page scroll.
  No framework, no build tooling beyond `tools/build.py`.
- A new problem should need at most four files in its folder. If it needs more, simplify the tooling first.

## Where things are
- `seed/`: the finished Rotting Oranges page and its tested C++ solution. Use them as the reference for style and content.
- `problems/<NNN-slug>/`: one folder per problem.
- `site/`: generated output.
- `tools/`: build and test scripts.
