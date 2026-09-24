# Upstream absorption

Write Craft is a fusion layer, not an automatic mirror. Upstream files remain
unchanged under `upstreams/`; reviewed behavior is independently expressed in
the installable Skill. A source is not considered absorbed merely because its
repository is pinned.

| Source | Decision | V0.1 use | Deliberately not adopted |
| --- | --- | --- | --- |
| Anthropic `doc-coauthoring` | Partial, independent re-expression | Context-aware drafting and fresh-reader testing | Mandatory opt-in, 5–10 questions by default, section-by-section ceremony, host-specific artifact commands |
| Anthropic `internal-comms` | Reference only | Future format vocabulary | Weekly updates, newsletters, incident templates in the V0.1 trigger surface |
| `writing-clearly-and-concisely` | Partial, principles only | One topic per paragraph, concrete language, remove waste | English punctuation and grammar rules, universal active-voice enforcement, mandatory subagent copyedit |
| Composio `content-research-writer` | Reference only | Future public-article research review | Hook optimization, publishing checklist, invented example citations, broad blog routing |
| Arjun `plain-language` | Selective absorption | Preserve truth while translating jargon and the reader's path | English-specific sentence examples as reusable copy |

## Local behavior map

- `SKILL.md` owns routing, task modes, evidence boundaries, question policy,
  delivery order, and reference loading.
- `references/decision-documents.md` owns decision framing, information
  layering, scenario use, and decision-relevant technical constraints.
- `references/clear-chinese.md` owns Chinese expression, terminology, precision,
  and naturalness.
- `references/reader-testing.md` owns fresh-context acceptance and fallback.
- `references/source-map.md` records provenance and rejected behaviors for the
  installed product without requiring upstream files at runtime.

## Update policy

`scripts/upstream_status.py --remote --json` may report remote drift, but it
never updates a pin. A future update must review the exact commit range, revise
this matrix and the lock together, and rerun source, package, and behavioral
validation.
