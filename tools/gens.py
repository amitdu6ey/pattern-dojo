#!/usr/bin/env python3
"""Seeded input generators for tests.json. Standard library only.

A spec is a dict: {"gen": "array", "seed": 1, ...params}. A parameter written as [lo, hi] (two ints) is drawn from
that inclusive range, so one spec can describe many small random cases (fuzz). Same spec, same output, every time.

Output formats (the driver of each problem reads one of these):
  array        first line "n" (or "n k" when k is given), second line n integers
  grid         first line "R C", then R lines of C integers
  snake_grid   same format as grid: a serpentine corridor of fresh oranges (1) with a rotten orange (2) at the top left
  string       one line
  graph        first line "n m", then m lines "u v" or "u v w" (0-indexed)
  permutation  first line "n", second line a permutation of 1..n
"""
import random

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def _draw(value, rng):
    if isinstance(value, list) and len(value) == 2 and all(isinstance(x, int) for x in value):
        return rng.randint(value[0], value[1])
    return value


def _params(spec, rng):
    return {k: _draw(v, rng) for k, v in spec.items() if k not in ("gen", "seed")}


def _array(p, rng):
    n, lo, hi = p.get("n", 10), p.get("lo", 0), p.get("hi", 100)
    if p.get("distinct"):
        if hi - lo + 1 < n:
            raise ValueError("distinct needs hi - lo + 1 >= n")
        vals = rng.sample(range(lo, hi + 1), n)
    else:
        vals = [rng.randint(lo, hi) for _ in range(n)]
    if p.get("sorted"):
        vals.sort()
    head = "%d %d" % (n, p["k"]) if "k" in p else str(n)
    return head + "\n" + " ".join(map(str, vals)) + "\n"


def _grid(p, rng):
    rows, cols = p.get("rows", 5), p.get("cols", 5)
    values = p.get("values", [0, 1, 2])
    weights = p.get("weights", [1, 3, 1])
    lines = [" ".join(str(rng.choices(values, weights)[0]) for _ in range(cols)) for _ in range(rows)]
    return "%d %d\n" % (rows, cols) + "\n".join(lines) + "\n"


def _snake_grid(p, rng):
    """A serpentine corridor: full rows of 1 joined by a single gap in each wall row, so rot needs about
    rows * cols / 2 minutes to reach the end. Slow for solutions that rescan the whole grid every minute."""
    rows, cols = p.get("rows", 5), p.get("cols", 5)
    grid = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        if r % 2 == 0:
            grid[r] = [1] * cols
        else:
            grid[r][cols - 1 if (r // 2) % 2 == 0 else 0] = 1
    grid[0][0] = 2
    return "%d %d\n" % (rows, cols) + "\n".join(" ".join(map(str, row)) for row in grid) + "\n"


def _string(p, rng):
    n, alphabet = p.get("n", 10), p.get("alphabet", ALPHABET)
    return "".join(rng.choice(alphabet) for _ in range(n)) + "\n"


def _graph(p, rng):
    n, m = p.get("n", 6), p.get("m", 8)
    directed, weighted, wmax = p.get("directed", False), p.get("weighted", False), p.get("wmax", 10)
    edges, seen = [], set()

    def add(u, v):
        key = (u, v) if directed else (min(u, v), max(u, v))
        if u == v or key in seen:
            return False
        seen.add(key)
        edges.append((u, v, rng.randint(1, wmax)))
        return True

    if p.get("connected") and n > 1:  # a random tree first, so every node is reachable
        order = list(range(n))
        rng.shuffle(order)
        for i in range(1, n):
            add(order[rng.randrange(i)], order[i])
    max_edges = n * (n - 1) if directed else n * (n - 1) // 2
    m = min(m, max_edges)
    while len(edges) < m:
        add(rng.randrange(n), rng.randrange(n))
    lines = ["%d %d%s" % (u, v, " %d" % w if weighted else "") for u, v, w in edges]
    return "%d %d\n" % (n, len(edges)) + "\n".join(lines) + ("\n" if lines else "")


def _permutation(p, rng):
    n = p.get("n", 10)
    vals = list(range(1, n + 1))
    rng.shuffle(vals)
    return "%d\n%s\n" % (n, " ".join(map(str, vals)))


GENERATORS = {"array": _array, "grid": _grid, "snake_grid": _snake_grid, "string": _string, "graph": _graph, "permutation": _permutation}


def check_spec(spec):
    """Raise ValueError if the spec names an unknown generator."""
    if not isinstance(spec, dict) or spec.get("gen") not in GENERATORS:
        raise ValueError("unknown generator %r; known: %s" % (spec.get("gen") if isinstance(spec, dict) else spec,
                                                              ", ".join(sorted(GENERATORS))))


def generate(spec):
    """Return the input text for a spec."""
    check_spec(spec)
    rng = random.Random(spec.get("seed", 0))
    return GENERATORS[spec["gen"]](_params(spec, rng), rng)


def fuzz_inputs(fuzz):
    """fuzz is {"runs": N, "seed": S, "spec": {...}}. Returns N input texts, each from its own seed."""
    base = dict(fuzz["spec"])
    out = []
    for i in range(fuzz["runs"]):
        base["seed"] = fuzz.get("seed", 0) + i
        out.append(generate(base))
    return out


if __name__ == "__main__":
    import sys
    print(__doc__)
    if len(sys.argv) > 1:
        import json
        print(generate(json.loads(sys.argv[1])))
