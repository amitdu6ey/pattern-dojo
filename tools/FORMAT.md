# Problem format

A problem is five files in `problems/<NNN-slug>/`. The folder name is the problem id. A worked example that the tests
use is in `tools/fixtures/pair-sum/`. Validate with `python3 tools/problem.py <dir>`.

## `solution.cpp`, `brute.cpp`, `driver.cpp`
- `solution.cpp`: the reference. It defines the function and includes its own headers.
- `brute.cpp`: a correct but naive version with the same signature. It must fail the scale tests for each enforced
  dimension (time: too slow; space: too much memory).
- `driver.cpp`: reads one test input from stdin, calls the function, prints the answer. It starts with
  `#include "solution.cpp"`. To run a candidate, copy it to `solution.cpp` in a temp folder next to the driver and
  compile `driver.cpp`. This is how the build runs the reference and the brute force, and how the judge runs a
  learner's code. The driver uses `std::` names and does not rely on `using namespace std`.

## `problem.json`
| Field | Type | Notes |
|---|---|---|
| `id` | string | Equals the folder name. |
| `title`, `pattern`, `difficulty`, `level` | strings | `difficulty` is easy, medium or hard. `level` is basic, variant or combined. |
| `tags`, `concepts` | string lists | `concepts` names banks in `tools/concepts/` (for example `heap`). |
| `statement` | string | In your own words. |
| `input_format`, `output_format` | strings | What the driver reads and prints. |
| `examples` | list | Each has `input`, `output` and `explain`. At least one. |
| `constraints` | list of strings | |
| `idea`, `naive` | strings | The idea in plain language, and why the naive approach is slow. |
| `hints` | list of strings | At least three, from gentle to strong. |
| `complexity` | object | `time`, `time_why`, `space`, `space_why`. |
| `mistakes` | list of strings | At least two. |
| `starter` | string | C++ code shown in the editor. It includes the headers the function needs. |
| `time_limit_ms`, `memory_limit_mb` | integers | Time limit per test, and peak memory limit. |
| `enforce` | object | `time` and `space` booleans. A dimension set to false needs a written `time_reason` or `space_reason`. |
| `quiz` | list | At least four multiple-choice questions, including tags `Time complexity` and `Space complexity`. Each has `tag`, `q`, four distinct `options`, `answer` (0 to 3) and `explanation`. |
| `walkthrough` | list | At least three steps, each `{"tab", "lines": [first, last], "text"}`. Lines are 1-based and refer to `solution.cpp`, which is shown with these steps after the learner solves the problem. |
| `interview` | object | `clarifications` (at least three, each with a regex `match` and an `answer`), `nudges` (exactly two), `followup` (`question` and `discussion`), `edge_cases` (at least two). |

## `tests.json`
```json
{
  "cases":  [{"name": "...", "input": "...", "expected": "...", "visible": true}],
  "scale":  [{"name": "...", "label": "a large input", "spec": {"gen": "array", "seed": 7, "n": 200000}}],
  "fuzz":   {"runs": 60, "seed": 500, "spec": {"gen": "array", "n": [1, 12]}}
}
```
- `cases`: hand-written. At least five, at least two visible and one hidden. Names are unique. These run on Run
  (visible only) and Submit (all).
- `scale`: large generated inputs. Expected output comes from the reference. The reference must pass them inside the
  limits and the brute force must fail them (see the gates). The `label` is all a learner sees for a failure.
- `fuzz`: many small random inputs, used to check the brute force against the reference. Required.
- A generator parameter written as `[lo, hi]` is drawn from that inclusive range per run.
- Generators live in `tools/gens.py`: `array`, `grid`, `string`, `graph`, `permutation`. Add new ones there, with a
  test in `tools/test_tools.py`.

## Build gates (`python3 tools/build.py --check [--root DIR] [id ...]`)
1. The reference passes every hand case and scale case inside the limits.
2. The brute force agrees with the reference on all hand cases and on the fuzz inputs.
3. For each enforced dimension, the brute force fails at least one scale test (TLE for time, MLE for space).
   Otherwise the build fails with "tests do not enforce the intended complexity".
