# Source map

This file records method provenance for maintainers. Write Craft remains usable
without any upstream checkout.

| Upstream | Reviewed capability | Local decision | Local expression |
| --- | --- | --- | --- |
| Anthropic `doc-coauthoring` | Context gathering, iterative structure, fresh-reader testing | Partial, independently expressed | `SKILL.md`, `reader-testing.md` |
| Anthropic Skill authoring guidance | Concise instructions, progressive references, representative input/output examples | Selectively adopted | `SKILL.md`, `decision-documents.md` |
| Anthropic agent-evaluation guidance | Separate capability from regression evidence; calibrate model graders with people | Development guidance only | `reader-testing.md`, repository evals |
| Anthropic `internal-comms` | Internal communication formats | Reference only for a later release | Not in the current trigger surface |
| `writing-clearly-and-concisely` | Topic-focused paragraphs, concrete language, concision | Language-neutral principles only | `clear-chinese.md` |
| Composio `content-research-writer` | Research-assisted articles and section feedback | Reference only; outside current scope | Not in the current trigger surface |
| Arjun `plain-language` | Explain technical material without deleting precision or uncertainty | Selectively absorbed under MIT | `decision-documents.md`, `clear-chinese.md` |
| Pi Skill documentation | Progressive Skill loading and package integration boundaries | Packaging and validation guidance only | Repository tooling; no runtime dependency |

The project also consulted public Microsoft guidance on scannable content and
Google developer-documentation accessibility guidance. Public method guidance
in this table is not vendored and is not a runtime dependency.

See the repository-level `upstreams.lock.json`, `THIRD_PARTY_NOTICES.md`, and
`docs/upstream-absorption.md` for exact revisions and license handling.
