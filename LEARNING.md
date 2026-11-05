# Learning strategy (DSA only)

Scope for now: data structures and algorithms. System design, behavioural rounds and language trivia are out of scope.

Nobody can see inside one person's brain. These are the best-supported general methods, and the platform measures
your own results (solve grades, error causes, calibration) to tune them for you over time. Citations are author and
year only; check them before quoting.

## Principles and how the platform applies them

| Principle | Evidence | What the platform does |
|---|---|---|
| Retrieval practice beats rereading | Roediger and Karpicke 2006; Dunlosky et al. 2013 rate practice testing high utility | Attempt first. A problem opens on the statement and a blank editor. Hints and the walkthrough are gated and logged. A review means solving again from a blank editor, never rereading. |
| Spaced practice | Cepeda et al. 2006; Dunlosky et al. 2013 rate distributed practice high utility | Re-solve at 1, 3, 7, 16, 35 and 90 days. The interval depends on the grade of the last solve: unaided, with hints, slow, or failed. |
| Interleaving | Rohrer and Taylor 2007; Dunlosky et al. 2013 rate it moderate | Sessions mix patterns. Before coding, you name the pattern and say why. Choosing the pattern is the skill interviews test. |
| Desirable difficulty | Bjork 1994 | Pick problems you can solve with effort. A failed attempt is useful data, not a setback. New problems are chosen to keep success high but not certain. |
| Worked examples, then fade | Sweller and Cooper 1985; Renkl 2014 | After a failed attempt or a give-up, study the walkthrough, then re-solve a variant on a short interval. |
| Self-explanation | Chi et al. 1989 | The plan stage needs your approach written in words before you code. |
| Check understanding after success | Retrieval practice again; passing tests does not prove you know why it works (Roediger and Karpicke 2006; Chi et al. 1989) | After an accepted solution, multiple-choice questions on time and space complexity, the data structure used and the pattern. A wrong answer marks the solve shaky and shortens the review interval. |
| Calibration | Metacognition research; people tend to overrate what they have only reread | Rate your confidence before Submit. The platform shows how well your ratings match outcomes. |
| Error analysis | Deliberate practice (Ericsson et al. 1993) | After a miss, record the cause: misread, wrong pattern, missed edge case, bug, or too slow. The weakest causes get targeted. |
| Practise as you will be tested | Transfer-appropriate processing (Morris, Bransford and Franks 1977) | Interview mode: timed, staged, no autocomplete, scripted clarifications, limited nudges, follow-ups, a debrief. Scale tests use large inputs so a solution with the wrong complexity fails, as it would in a real round. |

## One interview round here
Default 40 minutes, no solution access, nudges limited to two and logged. Suggested time boxes:

| Stage | Minutes | You do |
|---|---|---|
| Clarify | 3 to 5 | Ask the questions a candidate should ask. The interviewer answers from a script. |
| Plan | 5 to 8 | Write the approach, a brute-force baseline, the better idea and its complexity, before any code. |
| Code | 15 to 20 | Write the solution. Run only on the visible examples. |
| Test | 5 | Write at least two test cases of your own and say what each checks. |
| Complexity | 2 | State time and space and justify them. |
| Follow-up | 5 | Answer one scripted follow-up (a variant or a scale question). |

The debrief scores problem solving, coding, verification (testing), communication (the quality of your written plan)
and time, lists the nudges used, and compares your confidence rating with the result. Then it schedules the review.

## What this cannot reproduce
A real person interrupting, reading your face, or asking an unscripted follow-up. Spoken explanation is also not
covered; the plan stage is a typed stand-in. Do a live mock with a peer or mentor regularly alongside this.

## A good session
One timed interview round, up to two reviews that are due, and one new problem. Roughly two hours, adjustable.
