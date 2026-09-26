# Upstream absorption

Write Craft is a fusion layer, not an automatic mirror. Upstream files remain
unchanged under `upstreams/`; reviewed behavior is independently expressed in
the installable Skill. A source is not considered absorbed merely because its
repository is pinned.

| Source | Decision | Current local use | Deliberately not adopted |
| --- | --- | --- | --- |
| Anthropic `doc-coauthoring` | Partial, independent re-expression | Context-aware drafting and fresh-reader testing | Mandatory opt-in, 5–10 questions by default, section-by-section ceremony, host-specific artifact commands |
| Anthropic `internal-comms` | Reference only | Future format vocabulary | Weekly updates, newsletters, and incident templates in the current trigger surface |
| `writing-clearly-and-concisely` | Partial, principles only | One topic per paragraph, concrete language, remove waste | English punctuation and grammar rules, universal active-voice enforcement, mandatory subagent copyedit |
| Composio `content-research-writer` | Reference only | Future public-article research review | Hook optimization, publishing checklist, invented example citations, and broad blog routing |
| Arjun `plain-language` | Selective absorption | Preserve truth while translating jargon and the reader's path | English-specific sentence examples as reusable copy |

## Local behavior map

- `SKILL.md` owns routing, task modes, evidence boundaries, question policy,
  delivery order, and reference loading.
- `references/decision-documents.md` owns decision framing, information
  layering, scenario use, and decision-relevant technical constraints.
- `references/clear-chinese.md` owns Chinese expression, terminology, precision,
  and naturalness.
- `references/document-presentation.md` owns platform-neutral visual hierarchy,
  semantic emphasis, and rendered-document verification; platform writes stay
  outside Write Craft.
- `references/source-integrity.md` owns faithful explanation, two-way coverage,
  relevant unknowns, and unresolved source conflicts.
- `references/reader-testing.md` owns fresh-context acceptance and fallback.
- `references/source-map.md` records provenance and rejected behaviors for the
  installed product without requiring upstream files at runtime.
- `scripts/validate.py` checks source and immutable historical evidence;
  `scripts/release_check.py` separately binds a release candidate to current
  behavior evidence.
- `scripts/eval_contracts.py` owns the shared deterministic source, digest, and
  status primitives. `scripts/eval_behavior.py` owns the v2 compatibility
  adapter, v3 evaluation flow, fact review, and optional blind-reader review.
  `scripts/eval_structured_output.ts` gives those isolated review stages three
  schema-bound terminating submission tools; Python still enforces the
  case-specific contracts after extraction. These are development tools, not
  installed Skill requirements.
- `evals/release-policy.json` fixes the current release evidence contract;
  changing the policy is a reviewed product decision, not a way to waive a
  failing candidate.

## Update policy

`scripts/upstream_status.py --remote --json` may report remote drift, but it
never updates a pin. A future update must review the exact commit range, revise
this matrix and the lock together, and rerun source, package, and behavioral
validation.
