# Source map

This file records method provenance for maintainers. Write Craft remains usable
without any upstream checkout.

| Upstream | Reviewed capability | Local decision | Local expression |
| --- | --- | --- | --- |
| Anthropic `doc-coauthoring` | Context gathering, iterative structure, fresh-reader testing | Partial, independently expressed | `SKILL.md`, `reader-testing.md` |
| Anthropic `internal-comms` | Internal communication formats | Reference only for a later release | None in V0.1 |
| `writing-clearly-and-concisely` | Topic-focused paragraphs, concrete language, concision | Language-neutral principles only | `clear-chinese.md` |
| Composio `content-research-writer` | Research-assisted articles and section feedback | Reference only; outside V0.1 | None in V0.1 |
| Arjun `plain-language` | Explain technical material without deleting precision or uncertainty | Selectively absorbed under MIT | `decision-documents.md`, `clear-chinese.md` |

V0.1 also consulted the public Microsoft guidance on scannable content and the
Google developer documentation accessibility guidance. They inform general
scannability checks but are not vendored repositories or runtime dependencies.

See the repository-level `upstreams.lock.json`, `THIRD_PARTY_NOTICES.md`, and
`docs/upstream-absorption.md` for exact revisions and license handling.
