# Log

One line per run: date, item, what changed, how it was verified.

- 2026-11-05 setup: repo created with the loop protocol, roadmap and the Rotting Oranges seed (page and C++ solution tested earlier on five grids).
- 2026-11-05 P0.1a: added tools/runner.py (compile and run C++ with time and memory limits, live memory watchdog, peak memory via wait4); verified by `--selftest`, 9 of 9 checks (OK, TLE, MLE, RE, OLE, CE, memory measurement). P0.1 split into P0.1a and P0.1b.
- 2026-11-05 setup: researched other DSA resources (RESEARCH.md), extended the roadmap (breadth batch, queue cap, predict-then-reveal visuals, prerequisites), created the public repo amitdu6ey/pattern-dojo and deployed a placeholder site to GitHub Pages. Verified: Actions run green (self-test on Linux, build, deploy) and the live URL serves the page.
- 2026-11-05 P0.1b: added the problem format (tools/FORMAT.md), validator (tools/problem.py), seeded generators (tools/gens.py) and a pair-sum fixture problem; 28 unit tests pass, including that the fixture's brute force agrees with the reference on fuzz inputs and times out on the scale test. P0.1 split further into P0.1c and P0.1d. LOOP.md made safe for cloud runs.
