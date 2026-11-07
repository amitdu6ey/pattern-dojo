# Loop protocol

Read this first on every run. One run advances the platform by exactly one ROADMAP item.

## Steps
0. Run `git pull --ff-only origin main`. A cloud run starts from a fresh checkout and a local run may be behind.
1. Read `state.json`.
   - `status` is `working` and `started_at` is less than 40 minutes ago: another run is in progress.
     Do nothing, say so in one line, and end the turn.
   - `status` is `working` and older than 40 minutes: the last run died. Add a line to `LOG.md`,
     set status to `idle`, and continue.
2. Take the first unchecked item in `ROADMAP.md`, top to bottom. If none are left, stop the loop and report.
3. Set `state.json` to `working` with `current` and `started_at` (`date -u +%FT%TZ`). Commit that change on its own
   (`git commit -am "lock: <item id>"`) and `git push origin main`, so any other runner sees the lock.
4. Do the item. One item per run. If it is too big for one run, split it into sub-items in `ROADMAP.md`,
   and do only the first.
5. Gate: `python3 tools/gate.py` runs every check (unit tests, runner self-test, fixture and problem checks, site
   build) and exits non-zero at the first failure. A gate that fails or flakes is a bug to find, never to rerun until
   it passes.
6. Bookkeeping, before the gate: tick the item in `ROADMAP.md`, append one line to `LOG.md` (date, item, what changed,
   how it was verified), and set `state.json` to `idle` with `last_run`. Then commit and push in ONE command, so
   that a failing gate can never be followed by a commit:
   `python3 tools/gate.py && git add -A && git commit -m "<item id>: <summary>" && git push origin main`
   Never split this across lines, never put a heredoc in the middle of it, never pipe the gate through `tail` or
   `grep`, and never run `git commit` on its own after a gate run. If the push is rejected, run
   `git pull --rebase origin main`, then the same one-line command again. If that fails, write what happened in
   `LOG.md`, set the state to `idle`, and end the run.
7. Reply with two lines at most: what you did, and the next item.

## Hard rules
- The repo is public at `github.com/amitdu6ey/pattern-dojo` and deploys to GitHub Pages on every push to `main`.
  The only push allowed is `git push origin main`, after the gate passes. Never force-push, never add another
  remote, never rewrite history. Never publish an Artifact, create accounts, or enter credentials.
- Everything committed is public. No personal data, secrets or tokens. Nothing copied from other sites.
- Pages serves the site read-only. Running and submitting code needs the local judge, so the site must say so.
- The loop never fetches from LeetCode or any other site. Live fetching is a command the user runs. Build and
  test the fetcher against recorded fixtures that you write by hand and mark clearly as samples. Never present
  fixture data as real.
- Python is stdlib only (3.9). C++ is C++17 built with `g++`. No pip, no npm, no downloads.
  The static site may load Google Fonts and nothing else from the network.
- Do not spawn subagents. Keep chat output short; put detail in the repo.
- Temporary files go in a folder made with `mktemp -d`, never in the repo.

## Where this runs
The loop may run on the user's machine or in an Anthropic cloud session that has only a fresh checkout of this repo,
no home folder, and none of the user's settings. So everything you need is in this repo, paths are relative to the
repo root, and `python3` and `g++` are expected. If either is missing, write that in `LOG.md` and stop; never skip
the gate. Both Linux and macOS must work.

## Product rules (from the user)
- DSA only for now. Desktop only: design for widths of 1100px and up, and do no mobile layout work.
- The interface is minimal. One column on the home screen, plain type, generous whitespace, only the controls a
  screen needs. No hero banners, badges, stat tiles, decorative cards, gradients, decorative icons, or animation
  beyond what teaches (the grid stepper is the exception). Prefer a list to a grid of cards and a link to a button.
  When unsure, leave it out. Reuse only the palette tokens and fonts from `seed/rotting-oranges.html`.
- The problem screen is a split view: the problem on the left, the editor, Run, Submit and results on the right.
  Each pane scrolls on its own. The page itself does not scroll.
- The learner writes C++ in the page and submits it. Submitting runs every test, including scale tests.
- After a Submit where every test passes, ask multiple-choice questions before unlocking the walkthrough:
  time complexity, space complexity, the pattern or the reason, an edge case, and generic questions about the data
  structures the solution uses (a heap solution gets heap questions).
- Follow `LEARNING.md`: attempt first, gated hints, graded solves, spaced re-solving, interview mode that
  feels like a real round. Features must trace back to it.
- `design/ui-mock.html` is the reference for look and structure. Its Run, Submit, interviewer and quiz are simulated.

## Problem quality bar
- A problem is five files in `problems/<NNN-slug>/`: `problem.json`, `tests.json`, `solution.cpp`, `driver.cpp`,
  `brute.cpp`. Describe the format in `tools/build.py` and keep it simple.
- Statements are in your own words. Never copy a platform's wording. Name the problem and link by title and
  number only.
- C++17, explicit includes (no `bits/stdc++.h`), compiled and run by the build. A solution that has not run is not done.
- Tests: at least 5 small hand cases including edge cases, a random small cross-check of the reference against
  `brute.cpp`, and scale tests generated with `tools/gens.py` (expected output comes from the reference). Size the
  scale tests so the reference passes inside the limits and `brute.cpp` fails them: TLE to enforce time, MLE to
  enforce space. If a dimension cannot be enforced by tests, set `enforce.<dimension>` to false with a written
  reason. Never skip silently. The build fails if the brute force passes every scale test for an enforced dimension.
- Limits live in `problem.json` as `time_limit_ms` and `memory_limit_mb`. Measure memory per test with
  `os.wait4` (`ru_maxrss`, bytes on macOS) and judge it after the run. macOS does not enforce memory limits, so a
  wall-clock timeout kills runaways.
- Quiz: time complexity, space complexity, one pattern or reason question, one edge-case question, plus
  `concepts` that pull from `tools/concepts/<name>.json`. Four options each, exactly one correct, an explanation,
  and distractors that are plausible common mistakes.
- Interview script in `problem.json`: likely clarifying questions with the interviewer's answers, two escalating
  nudges, one follow-up with its discussion, and an edge-case checklist.
- The page covers: the idea in plain language, why the naive approach is slow, the pattern, gated hints, an
  annotated solution, complexity with the reason, and the common mistakes.

## Where things are
- `LEARNING.md`: the learning strategy and the interview round design.
- `design/ui-mock.html`: the UI reference.
- `seed/`: the finished Rotting Oranges page and its tested C++ solution, used as the content and style reference.
- `problems/<NNN-slug>/`: one folder per problem. `site/`: generated output. `tools/`: build, judge and fetch scripts.
