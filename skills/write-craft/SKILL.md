---
name: write-craft
description: 将复杂技术方案、项目提案和工程说明重组为非技术决策者可理解、可判断、可行动的中文文档；用于老板版改写、立项或决策文档、技术转业务说明及相应审稿。不要用于广告创意、产品 UI 微文案、纯文件排版、飞书平台操作或面向开发者的 API 文档。
---

# Write Craft

Write for the reader's decision, not for the author's implementation history.
Improve the argument and information order before polishing sentences. Preserve
the truth: clearer prose must not hide uncertainty, cost, risk, constraints, or
missing evidence.

## Choose the task mode

- **Rewrite** when the user supplies an existing draft. Read the complete source
  before asking questions. Preserve supported facts and intent, then deliver the
  complete revised document first unless the user asks for diagnosis only.
- **Draft** when the user supplies notes or source material. If the material is
  sufficient, produce a useful first draft without asking the user to opt into a
  workflow.
- **Diagnose** when the user asks what is wrong, why a reader is confused, or
  how to improve the document. Explain the highest-impact structural,
  evidentiary, and language problems. Do not silently rewrite the whole document.

Use the user's requested format and language. When the user writes in Chinese
and gives no contrary direction, write natural Simplified Chinese.

## Build the writing contract

Before drafting, determine from the supplied material:

1. the primary reader and what they already know;
2. what the reader should understand, decide, approve, or do;
3. the load-bearing recommendation or conclusion;
4. the evidence and constraints that support or limit it;
5. the requested deliverable, length, tone, and platform constraints.

Treat an explicit length limit as a hard deliverable constraint. Unless the
user limits only a named section, the limit applies to the entire user-visible
answer, including titles, headings, table text, appendices, notes, caveats,
change explanations, and unresolved items. Budget space across those parts;
do not exceed the limit and then label the overflow as outside the “main text”.
Compress structure and wording before dropping decision-changing evidence. If
the critical facts still cannot fit, surface that conflict instead of silently
omitting them or overrunning the limit.

Do not repeat questions whose answers are already present. Ask only when a
missing answer can materially change the conclusion, scope, cost, acceptance,
or risk. Group at most three critical questions. If work can proceed safely,
mark the gap as `待确认` and deliver the draft instead of blocking.

## Separate claims before improving prose

Internally classify material as:

- confirmed fact or observed state;
- judgment or recommendation;
- goal or intended outcome;
- assumption or hypothesis to test;
- unknown or missing decision input.

Do not expose this ledger unless it helps the user. Never turn a goal into an
observed result, an expectation into a promise, a generated artifact into a
business outcome, or an unknown into a plausible-sounding number. Preserve
source attribution when the document depends on external evidence.

## Rebuild for the reader

Lead with the bottom line that the reader needs. A decision document normally
lets a scanning reader find the problem, recommendation, strongest reason,
material uncertainty, and requested decision before implementation detail.

Use an end-to-end scenario when it clarifies who uses the proposal, what they
do, what the system or team does, and what result is reviewed. Then place scope,
non-goals, delivery stages, acceptance, resources, trade-offs, risks, and
fallbacks at the depth the decision needs. Do not force every document into the
same headings.

Move implementation detail to an appendix only when it does not change the
decision. A technical constraint stays in the main body when it affects cost,
schedule, feasibility, risk, quality, compliance, or what must be approved.

For substantial decision writing or restructuring, read
[references/decision-documents.md](references/decision-documents.md).

## Make the language clear without hollowing it out

Prefer explicit actors, actions, conditions, and results. Give each paragraph
one job. Replace a technical term when a plain equivalent is accurate; explain
it once when the reader needs the term again; cut it when it serves only the
author. Keep exact numbers, conditions, uncertainty, and the distinction between
`不能` and `尚未`.

Do not use abstract words such as “赋能”“闭环”“智能化”“全面提升” as substitutes
for a mechanism, owner, result, or test. Do not infantilize a non-technical
reader or remove precision merely to shorten the document.

For Chinese drafting or sentence-level editing, read
[references/clear-chinese.md](references/clear-chinese.md).

## Deliver in the order the request needs

When the user asks for a draft or rewrite, default to:

1. the complete usable document;
2. a short explanation of the most consequential changes when it helps review;
3. unresolved items that can change the decision, clearly labeled;
4. reader-test results or a reusable fresh-context test prompt when requested
   or when the document is consequential enough to warrant it.

Do not prepend a long process explanation. Do not invent an approval request
when the source is only a status update. Preserve the author's voice when a
sample exists; clarity is not permission to replace it with a generic corporate
voice.

## Test the reader, not the intention

For a consequential final document, read
[references/reader-testing.md](references/reader-testing.md). Use a genuinely
independent context only when that capability is available and authorized. If
it is unavailable, provide the standalone prompt from that reference; do not
claim that an independent test ran.

Before delivery, confirm that a reader can identify:

- what problem or opportunity matters;
- what is recommended and why;
- what is in and out of scope;
- what evidence is known and what remains unverified;
- what resources, risks, and trade-offs matter;
- what, if anything, they must decide or do next.

Read [references/source-map.md](references/source-map.md) only when maintaining,
auditing, or explaining Write Craft's upstream provenance.
