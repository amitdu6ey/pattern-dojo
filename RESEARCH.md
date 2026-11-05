# What other DSA resources do, and what we take from them

Studied on 2026-11-05 from public pages and third-party summaries. Several official pages (NeetCode's roadmap,
Striver's sheet) could not be read directly, so statements about them come from secondary sources and are marked.
Nothing here is copied from those sites: this is a comparison, and every problem and explanation in this repo is
written from scratch.

## Resources and what they teach us

| Resource | What it does well | Limits worth designing around | What we take |
|---|---|---|---|
| NeetCode 150 and Blind 75 ([overview](https://www.educative.io/blog/neetcode-roadmap), [comparison](https://www.techinterview.org/post/3233474682/leetcode-patterns-by-frequency/)) | A curated list in a suggested order; the 150 extends the Blind 75 with dynamic programming, backtracking, graphs, heaps, tries and intervals. | Summaries disagree on whether the order is a real learning sequence. It assumes you already know the basics (secondary sources). | A curated, ordered list with explicit prerequisites between patterns. |
| AlgoMonster ([roadmap](https://algo.monster/problems/roadmap), [critique](https://prachub.com/resources/are-algomonster-s-48-coding-patterns-enough-for-technical-interviews)) | Pattern-first with a template per pattern, moving from basic problems to variations to combined patterns. | Paid. Reviewers warn that memorising templates is not the same as understanding. Vendor claims are unverified. | The progression basic, variant, combined inside each pattern. Our post-solve quiz and mixed review exist to counter memorisation. |
| Striver's A2Z sheet ([third-party repo](https://github.com/CodeWithSameer04/Striver-A2Z-DSA-Sheet)) | A long, step-by-step path from basics through sorting, arrays, binary search, recursion, linked lists, stacks, trees, graphs and dynamic programming, 450+ problems. | Sheet only; practice happens elsewhere. The canonical page could not be confirmed. | A foundations-first order, and the idea that breadth matters. We grow toward roughly 100 to 150 problems. |
| Tech Interview Handbook ([coding signals](https://www.techinterviewhandbook.org/coding-signals/)) | Free and open. Names what interviewers score: communication, problem solving, technical competence, testing. | No interactive coding or practice; reviewers say it is aimed at large tech companies. | The four signals as our debrief rubric. Testing is its own stage in our interview mode. |
| Interviewer write-ups ([an interviewing.io interviewer](https://dev.to/mortoray/how-i-evaluate-you-in-a-code-interview-42hh), [Google rubric via Exponent](https://www.tryexponent.com/blog/google-coding-interview-rubric)) | Show that scoring covers algorithms, coding, communication and problem solving, and that communication shapes how the rest is read. | Wording varies by company and level; some sources are secondhand. | Score communication explicitly (the typed plan stands in for speech). Count hints used. |
| Spaced-repetition tools for LeetCode ([guide](https://www.redgreencode.com/leetcode-tip-9-spaced-repetition/), [another](https://leetsrs.pages.dev/blog/spaced-repetition-for-leetcode)) | Re-solve on an expanding schedule, rate each attempt. | The exact day counts are conventions, not study results for interview prep. Queues can overflow and cause burnout. | Grade-based intervals, a capped review queue, and a way to retire a problem. |
| VisuAlgo and algorithm-visualization research ([VisuAlgo](https://visualgo.net), [meta-study](https://www.academia.edu/15636659/A_Meta_Study_of_Algorithm_Visualization_Effectiveness)) | Interactive animations plus quizzes. | Results are mixed; how engaged the learner is matters more than the animation. Some studies found weaker performance on theory questions. | Visuals only with active engagement: predict the next state before it is shown, and pair every visual with a question. |

## Where we aim to be different
These are goals, not claims. From what the sources above show, most resources cover some of this but not all of it together.
1. A real judge for the learner's own C++ with scale tests that make the intended time and space complexity necessary.
2. Post-solve multiple-choice questions on complexity and the data structures used, so a pass is not mistaken for understanding.
3. An interview mode with stages, scripted clarifications, limited nudges, follow-ups and a rubric-based debrief.
4. Graded, spaced re-solving with a capped queue.
5. A trending view of what companies are asking, drawn from LeetCode discussions (run by the user, sample data until then).
6. Minimal, fast, free and open.

## Honest gap
Content breadth. The established lists run to 150 to 450 problems. This project starts at 62 and the roadmap extends it
toward about 100. "Best" will depend on content depth and quality as much as on the features above.

## Changes made to the roadmap because of this research
- Review queue capped, with a retire option (spaced-repetition burnout).
- Visualizers use predict-then-reveal, and each is paired with a question (visualization research).
- Pattern prerequisites and a basic, variant, combined level on each problem (NeetCode and AlgoMonster ordering).
- Debrief rubric aligned with the four interview signals; hint count scored.
- A second batch of problems for breadth.
