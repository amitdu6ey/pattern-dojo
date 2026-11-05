# Roadmap

Scope: DSA only, desktop only. The strategy is in `LEARNING.md`. The experience should feel as close to a real
interview round as a website allows.

Goal: a static, free-to-host DSA prep platform. It teaches by pattern: the idea first, a tested C++ solution, and
spaced re-solving so patterns stick. Learners write and submit their own C++ in the page. A small local judge
(`tools/serve.py`) compiles and tests it, because C++ cannot run on static hosting. The loop takes the first
unchecked item each run (see `LOOP.md`).

## Phase 0: foundation
- [x] P0.1a `tools/runner.py`: compile C++ and run it with time and memory limits (peak memory from `os.wait4`,
      a live memory watchdog because macOS ignores `RLIMIT_AS`, verdicts OK, TLE, MLE, RE, OLE and CE), with a
      `--selftest` that proves each verdict on small programs. Split out of P0.1; the judge and the build share it.
- [x] P0.1b Problem format and tooling: `tools/FORMAT.md` (the spec), `tools/problem.py` (loader and validator),
      `tools/gens.py` (seeded generators with ranged parameters for fuzz tests), and a fixture problem in
      `tools/fixtures/pair-sum/`. Unit tests in `tools/test_tools.py`.
- [x] P0.1c `tools/build.py`, gates 1 and 2, using `tools/runner.py`: for every problem, compile `driver.cpp` with the
      reference as `solution.cpp`, run every hand case and scale case inside the limits and compare to expected
      (scale cases take their expected output from the reference); then check the brute force against the reference
      on all hand cases and on the fuzz inputs. Report per problem. Include `--check` (build and test, write
      nothing) and a problem filter. Test it on the fixture, including a deliberately wrong reference.
- [ ] P0.1d Gate 3 in `tools/build.py`: for each enforced dimension the brute force must fail at least one scale test
      (TLE for time, MLE for space), otherwise the build fails with "tests do not enforce the intended complexity".
      Also require the reference to use at most half the time limit on scale tests. Then write `site/` (a stub page
      per problem is enough; the real templates are P0.2 and P0.3). Test it on the fixture with a brute force that
      is accidentally fast.
- [ ] P0.2 Shared theme and layout from `seed/rotting-oranges.html` (palette tokens and fonts only, light and
      dark), following `design/ui-mock.html`: a single column of plain lists for the home screen, no decoration.
      Plus an `index.html` listing patterns and problems.
- [ ] P0.3 Problem page as a split view (problem left, editor and results right, each pane scrolling on its own).
      Statement, example, gated hints, and the annotated solution walkthrough with step tabs (locked until the
      learner has solved the problem and finished the quiz, or explicitly gives up). Port Rotting Oranges in as
      problem 001 with all five files, scale tests that its brute force fails, a quiz and an interview script,
      and keep its grid stepper in the walkthrough.
- [ ] P0.4 Local judge, `tools/serve.py` (stdlib): serves `site/` and exposes `/api/run` (visible tests only) and
      `/api/submit` (all tests, scale tests included). Compile with `g++ -std=c++17 -O2` into a fresh temp
      directory with the problem's `driver.cpp`, run every test under the time limit, compare output, measure peak
      memory, and return a verdict per test: AC, WA, TLE, MLE, RE or CE (with the compiler message). Visible
      tests show input, expected and actual on failure. Hidden and scale tests show the verdict and a label only,
      for example "TLE on a large input: a slower approach will not finish here". Safety, all required: bind to
      127.0.0.1 only; generate a random token at startup, embed it in the pages the server serves, and require it
      on every API call; check the Host and Origin headers; cap request, source (64 KB) and output sizes; apply
      CPU and wall-clock limits; delete the temp directory afterwards. Document that submitted code runs on the
      user's machine with their privileges and that macOS does not enforce memory limits. Test it with the
      reference (must be AC) and with deliberately wrong, slow, memory-hungry, crashing and non-compiling sources.
- [ ] P0.5 Editor and Run/Submit in the right pane: a plain `<textarea>` (monospace, Tab inserts spaces, no
      library), starter code from `problem.json`, Run (visible tests) and Submit (all tests), one line for the
      verdict and a short per-test list, and drafts saved in `localStorage`. When the page is opened without the
      local judge, show one line saying so and offer to copy the code.
- [ ] P0.6 Post-submit quiz. After a Submit where every test passes, ask multiple-choice questions one at a time
      with instant feedback and an explanation: time complexity, space complexity, the pattern or reason, an edge
      case, and one or two concept questions drawn from the banks for the problem's `concepts` (a heap solution
      gets heap questions: push and pop cost, which kind of heap, why not sort). Write starter banks in
      `tools/concepts/` for queue-and-bfs, heap, stack, hash-map and binary-search: at least 8 questions each, in
      your own words, four options, one correct, an explanation, plausible distractors. Record every answer. A
      wrong answer marks the solve "shaky" and adds the concept to the review pool. Unlock the walkthrough after
      the quiz.
- [ ] P0.7 Progress and grading in `localStorage`. Statuses: solved, attempted, needs review. Each solve gets a grade:
      unaided, with hints, slow, shaky (quiz misses) or failed. Re-solve intervals follow the Leitner steps 1, 3, 7,
      16, 35 and 90 days, shortened by weaker grades. The home page shows the review queue as a plain list of
      re-solves plus missed concept questions. Cap the queue (default 6 due items, weakest first) and let the
      learner retire a problem, so reviews do not turn into burnout.
- [ ] P0.8 Interview mode core, following `LEARNING.md` and the mock: a timed round (40 minutes by default) on a
      problem the system picks (interleaved, weighted toward due reviews, weak patterns and company trending).
      Stages: clarify (scripted interviewer answers), plan (typed approach, brute force, better idea,
      complexity, required before coding), code (Run on visible examples only, no hints), test (at least two
      of the learner's own cases), complexity (typed statement, checked against the quiz answers), follow-up
      (scripted question). Two logged nudges at most. No walkthrough access during the round.
- [ ] P0.9 Interview debrief and calibration: a rubric aligned with the four interview signals (problem solving, technical competence, testing,
      communication) plus time and hints used,
      time spent per stage against the suggested boxes, nudges used, the learner's confidence rating compared with
      the outcome, an error-cause tag after a miss (misread, wrong pattern, missed edge case, bug, too slow),
      and the grade fed to the review scheduler.
- [ ] P0.10 README (short, minimal), quick start, project map, and a check that the deployed site matches the repo. The Pages workflow already exists; confirm the latest
      Actions run is green and the live URL serves the current build. State plainly that static hosting is read-only: running and submitting code needs the local
      judge from P0.4.
- [ ] P0.11 Trending pipeline: `tools/fetch_trending.py` (stdlib `urllib`). For each company in
      `tools/companies.json` (Microsoft, Google, Meta/Facebook, Stripe, Deliveroo, ShareChat, Amazon, Intuit,
      LinkedIn), read recent LeetCode discussion posts tagged with that company in the interview question and
      experience categories, extract the LeetCode problems each post mentions (problem links and "LC <number>"
      mentions), count mentions per problem per company inside a configurable window (default 90 days), and write
      `data/trending.json` (company -> ranked problems with mention count and date of the latest mention).
      Keep only titles, slugs, counts and links, never post bodies. Be polite: one request at a time, a delay
      between requests, a clear User-Agent, a hard cap on pages. Write and test it against hand-written recorded
      fixtures in `tools/fixtures/`. The loop must NOT call LeetCode. Ship `data/trending.json` as a clearly
      labelled sample built from the fixtures, never presented as real data. Document
      `python3 tools/fetch_trending.py --live` in the README as a command the user runs, and note that LeetCode's
      terms may limit automated access, so the user should check them first.
- [ ] P0.12 Trending UI as in the mock: company tabs, a ranked plain list with mention count and last-seen date, a
      "last updated" stamp, and a "sample data" note when the data is the fixture sample. Each row links to the
      LeetCode problem and, when we have our own page, to that page.
- [ ] P0.13 Map trending problems to patterns (`tools/patterns.json`; unknown ones show "unmapped") and add a
      "Practice what's trending" filter that orders our problems by mentions at the chosen company.

## Phase 1: patterns
Each problem is one item and includes everything in the quality bar: five files with scale tests that its brute
force fails, a quiz, an interview script, and the page. Problem titles are well-known interview problems. Write
every statement in your own words.
- [ ] P1.01 Arrays and hashing: Two Sum
- [ ] P1.02 Arrays and hashing: Group Anagrams
- [ ] P1.03 Arrays and hashing: Top K Frequent Elements
- [ ] P1.04 Arrays and hashing: Product of Array Except Self
- [ ] P1.05 Two pointers: Valid Palindrome
- [ ] P1.06 Two pointers: 3Sum
- [ ] P1.07 Two pointers: Container With Most Water
- [ ] P1.08 Two pointers: Trapping Rain Water
- [ ] P1.09 Sliding window: Best Time to Buy and Sell Stock
- [ ] P1.10 Sliding window: Longest Substring Without Repeating Characters
- [ ] P1.11 Sliding window: Minimum Window Substring
- [ ] P1.12 Sliding window: Sliding Window Maximum
- [ ] P1.13 Binary search: Binary Search
- [ ] P1.14 Binary search: Search in Rotated Sorted Array
- [ ] P1.15 Binary search: Koko Eating Bananas
- [ ] P1.16 Binary search: Median of Two Sorted Arrays
- [ ] P1.17 Stack: Valid Parentheses
- [ ] P1.18 Stack: Daily Temperatures
- [ ] P1.19 Stack: Largest Rectangle in Histogram
- [ ] P1.20 Stack: Min Stack
- [ ] P1.21 Linked list: Reverse Linked List
- [ ] P1.22 Linked list: Merge Two Sorted Lists
- [ ] P1.23 Linked list: Linked List Cycle
- [ ] P1.24 Linked list: LRU Cache
- [ ] P1.25 Trees: Maximum Depth of Binary Tree
- [ ] P1.26 Trees: Binary Tree Level Order Traversal
- [ ] P1.27 Trees: Validate Binary Search Tree
- [ ] P1.28 Trees: Lowest Common Ancestor
- [ ] P1.29 Graphs: Number of Islands
- [ ] P1.30 Graphs: Clone Graph
- [ ] P1.31 Graphs: Course Schedule (topological sort)
- [ ] P1.32 Graphs: Word Ladder
- [ ] P1.33 Union-Find: Number of Connected Components
- [ ] P1.34 Union-Find: Redundant Connection
- [ ] P1.35 Shortest paths: Network Delay Time (Dijkstra)
- [ ] P1.36 Shortest paths: Cheapest Flights Within K Stops
- [ ] P1.37 Heap: Kth Largest Element
- [ ] P1.38 Heap: Merge K Sorted Lists
- [ ] P1.39 Heap: Find Median from Data Stream
- [ ] P1.40 Heap: Task Scheduler
- [ ] P1.41 Intervals: Merge Intervals
- [ ] P1.42 Intervals: Insert Interval
- [ ] P1.43 Intervals: Meeting Rooms II
- [ ] P1.44 Intervals: Non-overlapping Intervals
- [ ] P1.45 Backtracking: Subsets
- [ ] P1.46 Backtracking: Permutations
- [ ] P1.47 Backtracking: Combination Sum
- [ ] P1.48 Backtracking: N-Queens
- [ ] P1.49 Dynamic programming 1D: Climbing Stairs
- [ ] P1.50 Dynamic programming 1D: House Robber
- [ ] P1.51 Dynamic programming 1D: Coin Change
- [ ] P1.52 Dynamic programming 1D: Longest Increasing Subsequence
- [ ] P1.53 Dynamic programming 2D: Unique Paths
- [ ] P1.54 Dynamic programming 2D: Longest Common Subsequence
- [ ] P1.55 Dynamic programming 2D: Edit Distance
- [ ] P1.56 Greedy: Jump Game
- [ ] P1.57 Greedy: Gas Station
- [ ] P1.58 Greedy: Partition Labels
- [ ] P1.59 Tries: Implement Trie
- [ ] P1.60 Tries: Word Search II
- [ ] P1.61 Bit manipulation: Single Number
- [ ] P1.62 Bit manipulation: Counting Bits

## Phase 1b: breadth
A second batch toward about 100 problems, same quality bar. Source: gaps found in `RESEARCH.md`.
- [ ] P1.63 Arrays and hashing: Contains Duplicate
- [ ] P1.64 Arrays and hashing: Valid Anagram
- [ ] P1.65 Arrays and hashing: Longest Consecutive Sequence
- [ ] P1.66 Arrays and hashing: Valid Sudoku
- [ ] P1.67 Two pointers: Two Sum II (sorted input)
- [ ] P1.68 Sliding window: Longest Repeating Character Replacement
- [ ] P1.69 Sliding window: Permutation in String
- [ ] P1.70 Binary search: Search a 2D Matrix
- [ ] P1.71 Binary search: Find Minimum in Rotated Sorted Array
- [ ] P1.72 Binary search: Time Based Key-Value Store
- [ ] P1.73 Stack: Evaluate Reverse Polish Notation
- [ ] P1.74 Stack: Generate Parentheses
- [ ] P1.75 Stack: Car Fleet
- [ ] P1.76 Linked list: Reorder List
- [ ] P1.77 Linked list: Remove Nth Node From End
- [ ] P1.78 Linked list: Add Two Numbers
- [ ] P1.79 Linked list: Copy List with Random Pointer
- [ ] P1.80 Linked list: Reverse Nodes in k-Group
- [ ] P1.81 Trees: Invert Binary Tree
- [ ] P1.82 Trees: Diameter of Binary Tree
- [ ] P1.83 Trees: Subtree of Another Tree
- [ ] P1.84 Trees: Kth Smallest Element in a BST
- [ ] P1.85 Trees: Construct Binary Tree from Preorder and Inorder
- [ ] P1.86 Trees: Binary Tree Maximum Path Sum
- [ ] P1.87 Trees: Serialize and Deserialize Binary Tree
- [ ] P1.88 Heap: K Closest Points to Origin
- [ ] P1.89 Backtracking: Word Search
- [ ] P1.90 Backtracking: Palindrome Partitioning
- [ ] P1.91 Graphs: Pacific Atlantic Water Flow
- [ ] P1.92 Graphs: Graph Valid Tree
- [ ] P1.93 Graphs: Alien Dictionary
- [ ] P1.94 Graphs: Min Cost to Connect All Points
- [ ] P1.95 Dynamic programming: Longest Palindromic Substring
- [ ] P1.96 Dynamic programming: Decode Ways
- [ ] P1.97 Dynamic programming: Word Break
- [ ] P1.98 Dynamic programming: Partition Equal Subset Sum
- [ ] P1.99 Dynamic programming: Best Time to Buy and Sell Stock with Cooldown
- [ ] P1.100 Greedy: Maximum Subarray
- [ ] P1.101 Greedy: Jump Game II
- [ ] P1.102 Math and matrices: Rotate Image
- [ ] P1.103 Math and matrices: Spiral Matrix
- [ ] P1.104 Math and matrices: Set Matrix Zeroes
- [ ] P1.105 Bit manipulation: Missing Number
- [ ] P1.106 Bit manipulation: Number of 1 Bits

## Phase 2: platform features
- [ ] P2.1 "Which pattern is this?" drill: show a statement, the learner names the pattern and the reason, then sees why.
- [ ] P2.2 Pattern cheat sheets: one page per pattern with the template code and when to reach for it.
- [ ] P2.3 Search and filter across problems by pattern, difficulty, status and company.
- [ ] P2.4 Interview extras: a two-problem onsite round (45 minutes each), company style presets (timing and
      follow-up depth), and optional local voice recording of the spoken plan (microphone, kept in the browser).
- [ ] P2.5 Reusable visualizers: array with pointers, binary tree, recursion tree, DP table. Wire them into earlier problems. Use predict-then-reveal (the learner predicts the next state before it is
      shown) and pair every visual with a question.
- [ ] P2.6 Stats page: solves per pattern, grade mix, error causes, calibration, weakest concepts.
- [ ] P2.7 More concept banks: trie, union-find, BST, graph traversal, sorting, recursion, dynamic programming, intervals.
- [ ] P2.8 In-browser JavaScript runner (Web Worker, with a timeout) so Run and Submit also work on static hosting
      for problems with a JavaScript reference. The C++ judge stays the main path. Say plainly that time and memory
      limits are weaker in the browser.

- [ ] P2.9 Prerequisite graph: declare which patterns depend on which (for example, binary search before
      rotated-array variants, BFS before shortest paths). Recommend a "next up" problem from the prerequisites
      and the learner's weakest patterns.
- [ ] P2.10 Add a `level` to each problem (basic, variant, combined) and order problems inside a pattern that
      way, with a short reusable template per pattern. Keep the quiz and mixed review so templates are understood,
      not just memorised.

## Phase 3: polish
- [ ] P3.1 Accessibility pass (keyboard, contrast, reduced motion) and a check at 1100px, 1440px and 1920px widths
      on every page. No mobile layout.
- [ ] P3.2 Performance pass; measure page weight and report it in the README.
- [ ] P3.3 Final README, LICENSE, and a CONTRIBUTING note on how to add a problem in five files.
