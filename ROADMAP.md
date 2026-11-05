# Roadmap

Goal: a static, free-to-host DSA prep platform. It teaches by pattern, with intuition first, an interactive
visual where it helps, a tested C++ solution, and spaced review so the patterns stick.
The loop takes the first unchecked item each run (see `LOOP.md`).

## Phase 0: foundation
- [ ] P0.1 `tools/build.py` (stdlib only): reads `problems/*/problem.json`, compiles each `solution.cpp` with
      g++ against `tests.json` cases, fails on any mismatch, and writes `site/`. Design it so a new problem needs
      at most four files. Include a `--check` flag that builds and tests without writing output.
- [ ] P0.2 Shared theme and layout, extracted from `seed/rotting-oranges.html` (palette tokens and fonts only, light
      and dark), kept minimal: one column, plain list navigation, no decoration. Plus an `index.html` that lists
      patterns and problems as a simple list.
- [ ] P0.3 Problem page template: statement, idea, hints that reveal one at a time, annotated solution with
      step tabs, complexity, mistakes. Port Rotting Oranges in as problem 001, including its grid stepper.
- [ ] P0.4 Progress tracking in `localStorage` (solved, attempted, needs review) and a review queue using the
      Leitner intervals 1, 3, 7, 16, 35 and 90 days, shown on the home page.
- [ ] P0.5 README with a hero, feature list, quick start and project map, plus a GitHub Pages workflow file
      (written only; never pushed).
- [ ] P0.6 Trending pipeline: `tools/fetch_trending.py` (stdlib `urllib`). For each company in
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
- [ ] P0.7 Trending UI: a "Trending by company" section on the home page with company tabs, ranked problems with
      mention count and last-seen date, a "last updated" stamp, and a "sample data" banner when the data is the
      fixture sample. Each row links to the LeetCode problem and, when we have our own page, to that page.
- [ ] P0.8 Map trending problems to patterns (`tools/patterns.json`; unknown ones show "unmapped") and add a
      "Practice what's trending" filter that orders our problems by mentions at the chosen company.

## Phase 1: patterns (each problem is one item: idea, visual if useful, tested solution, page)
Problem titles are well-known interview problems. Write every statement in your own words.
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

## Phase 2: platform features
- [ ] P2.1 "Which pattern is this?" quiz: show a problem statement, the learner picks the pattern, then sees why.
- [ ] P2.2 Pattern cheat sheets: one page per pattern with the template code and when to reach for it.
- [ ] P2.3 Search and filter across problems by pattern, difficulty and status.
- [ ] P2.4 Mock interview mode: random problem, countdown timer, reveal hints with a penalty, self-rating at the end.
- [ ] P2.5 Reusable visualizers: array with pointers, binary tree, recursion tree, DP table. Wire them into earlier problems.
- [ ] P2.6 Stats page: solved per pattern, review streak, weakest patterns.

## Phase 3: polish
- [ ] P3.1 Accessibility pass (keyboard, contrast, reduced motion) and a 400px phone pass over every page.
- [ ] P3.2 Offline support and performance pass; measure page weight and report it in the README.
- [ ] P3.3 Final README, LICENSE, and a CONTRIBUTING note on how to add a problem in four files.
