# Scenario-writing development check

Status: targeted calibration and fresh-case checks completed. The r30-r32
development failures below remain part of the record. This is not full release
evidence or a human-reader result.

## Changes

The existing decision-document reference now explains source-supported scenario
openings, real versus illustrative cases, deferred materials, and how to avoid
repeating a workflow in paragraphs, steps, and tables. A synthetic customer
support example teaches the behavior; a different warehouse scenario tests it.
No private business documents or media were added to the runtime or test set.

## Observed results

All calls used Pi `deepseek/deepseek-flash` for generation and judging, with raw
JSONL disabled. The local ignored artifacts are under
`.artifacts/write-craft-evals/`:

| Run | Machine result | Author inspection |
| --- | --- | --- |
| `scenario-targeted-r30` | 3/3 PASS | Sparse-module and short-status cases passed. New scenario repeated its purpose and changed an unstated history into no historical records. Its PASS is disputed. |
| `scenario-targeted-r31` | 1/1 PASS | Repetition improved, but the draft inferred an existing item-by-item manual workflow from a time-saving goal. Its PASS is disputed. |
| `scenario-targeted-r32` | 1/1 PASS | Explicit proposed state, human decision, no stock mutation, deferred materials, and no approval request were preserved. A redundant second paragraph and irrelevant absent-information inventory remained. Its PASS is disputed. |

These are successive development candidates with strengthened instructions and
criteria, not independent repetitions of one frozen candidate. Do not aggregate
them into a success rate. The earlier two compatibility checks do not establish
full regression coverage for the final candidate.

Final r32 evidence: after a complete scenario the draft adds a second paragraph
beginning `这套助手承担的只是`, restating its purpose and human boundary. It also
lists unspecified historical errors and goods despite their irrelevance to the
explanation. The judge accepts these against the explicit anti-repetition and
absence-inventory criterion. Inspect the candidate, not only the PASS label.

## Checks and remaining work

Source validation, package-boundary validation, Skill metadata validation, and
35 repository tests passed during this change. Final source/package checks and
diff whitespace checks passed after the last instruction/contract edit.

## Calibration follow-up

Added four fixed fixtures: reject a redundant paragraph, reject an irrelevant
absence inventory, accept a concise scenario, and accept a repeated boundary
that adds an actual acceptance check. The judge prompt now requires an
information-contribution check when the contract prohibits repetition, while
preserving useful emphasis and avoiding universal style-based blocking.

- `scenario-judge-calibration-r33`: 15/15 fixtures matched expected judgments,
  including the existing 11 fixtures.
- `scenario-targeted-r32/business-scenario-with-deferred-materials--1/rejudge-1`:
  the unchanged actual failed draft now receives FAIL for both its redundant
  paragraph and irrelevant absence inventory. Original artifacts are retained.
- `scenario-verified-r34`: a fresh draft received PASS on its first attempt,
  with zero revisions. Author inspection confirms a single workflow, proposed
  state, preserved human decision and no stock mutation, time-saving target
  distinguished from measurement, deferred real materials, and no approval
  request. It still contains an unnecessary sentence explaining that the current
  manual workflow is unspecified; this is an editorial improvement opportunity,
  not proof of ideal concision or universal effectiveness.

All these calls used Pi `deepseek/deepseek-flash`, low thinking, with raw JSONL
storage disabled. Static validation, 35 local tests, packaging, and whitespace
checks passed after the judge change. The runtime Skill was not changed in this
calibration follow-up. These checks preceded the final regression below.

## Final regression before commit

`scenario-final-regression-r35` completed all 18 regression cases with PASS,
using the same Pi model and low-thinking settings. Seventeen passed without
revision; `ai-video-proposal-rewrite` required the configured single revision.
Skill SHA-256: `984b940d86934d20a5d72a1b878daf8f8a3a91accc8934dc33a5e9cd6cebaccb`.
Reported model cost: 0.162944852. Raw JSONL storage remained disabled.

The scenario draft was inspected: one use scenario, evidence/communication
purpose, and the deferred-material note, without a redundant workflow paragraph
or absence inventory. The presentation draft retained factual boundaries but
still repeated the historical-evidence caveat. That remains a prose-quality
limitation; machine contract PASS does not establish uniformly concise prose.

Source validation, 35 local tests, package validation (15 entries, 76,538
unpacked bytes), and diff checks passed. This batch is prepared for a local
scoped commit. Human reading, real-media cases, exploration on this candidate,
and release acceptance remain unverified. No installation, push, or release
was performed.

## Adjacent repetition follow-up

The presentation reference now checks adjacent sentences and paragraphs for
new information rather than merely different wording. The presentation case
explicitly prohibits redundant evidence paraphrases, without rejecting useful
independent summaries or acceptance checks. Two fixed fixtures preserve the
actual r35 draft and a counterpart with only its duplicate paragraph removed.

- `adjacent-repetition-calibration-r36`: 17/17 judgments matched expectations.
  The unchanged r35 draft received FAIL; deleting only the duplicate evidence
  paragraph produced PASS. Existing positive and negative fixtures also passed.
- `adjacent-repetition-regression-r37`: both the scenario and presentation cases
  passed on their first attempt, with zero revisions. The presentation draft no
  longer contains the duplicate evidence paragraph. It preserves the proposed
  state, workflow, human judgment, excluded scope, and unresolved commitments.

These calls used Pi `deepseek/deepseek-flash`, low thinking for generation and
fact judging, with raw JSONL storage disabled. Candidate Skill SHA-256:
`794ae923b9775569eeb9dc1e5c3e2d19713d5b7732e29ba02f79ed45d846ab01`.
Reported model costs were 0.014068683 for calibration and 0.022725183 for the
targeted regression. Source validation, 35 local tests, package validation
(15 entries, 76,973 unpacked bytes), and whitespace checks passed.

Inspection still finds opportunities for concision: the presentation heading
restates the evidence conclusion before the paragraph explains its basis, and
the scenario mentions the unspecified current manual workflow. The specific
duplicate-paragraph failure is now covered; uniformly concise prose is not
established. This was a two-case targeted regression, not a rerun of all 18
cases on this candidate. Independent reader stages and human reading were not
run. No Feishu edit, installation, push, or release was performed.
