---
name: write-craft
description: 将复杂技术方案、项目提案、阶段进展和工程说明重组为目标读者，尤其是非技术决策者，可理解、可判断、可行动的中文文档；用于老板版改写、立项或决策文档、不同读者版本、选项比较、技术转业务说明及相应诊断。不要用于广告创意、产品 UI 微文案、纯文件排版、飞书平台操作或面向开发者的 API 文档。
---

# Write Craft

Turn complex work material into a document the intended reader can understand
without the author's conversation history, judge accurately, and use directly.
Improve the argument and information order before polishing sentences. Preserve
the truth and the author's decisions: clearer prose must not hide uncertainty,
cost, risk, constraints, missing evidence, or an already approved boundary.

## Choose the task mode

- **Rewrite** when the user supplies an existing draft. Read the complete source
  before asking questions. Preserve supported facts and intent, then deliver the
  complete revised document first unless the user asks for diagnosis only.
- **Draft** when the user supplies notes or source material. If the material is
  sufficient, produce a useful first draft without asking the user to opt into a
  workflow.
- **Diagnose** when the user asks what is wrong, why a reader is confused, or
  how to improve the document. Explain the highest-impact structural,
  evidentiary, and language problems. Ground the diagnosis in observable
  features of the supplied document and its stated task, not an imagined
  reader's attention span, knowledge, or reaction. Do not silently rewrite the
  whole document.

When the user asks only whether several requests belong to Write Craft, give
the requested classification and one direct boundary reason for each item,
then stop. Do not turn a routing answer into a mode tutorial, an invitation to
send material, or an explanation of unrelated editing rules.

In Diagnose, use `observed feature -> possible comprehension risk -> supported
revision direction`. For example: “原稿先列实现组件，最后才说明业务目的” is an
observed feature; “这种顺序可能让读者更难在接触组件时判断这些信息为何重要”
is a bounded comprehension risk; “把原稿已有的业务目的移到组件说明之前” is a
supported direction. Do not replace that chain with claims about how bosses
usually read, what they know, or when they stop reading.

Keep the middle step explicitly conditional: use “可能让……更难定位” or
“读者可能需要先……再……”, not unqualified predictions such as “读者需要先……
之后才能……”, “读者无法理解”, or “只能读完全文才知道”. Describe a missing
relationship or reader task as a feature of the text, not as proof that a reader
must guess, cannot understand, or will not know how to respond. Diagnose only
what the supplied text or summary makes observable. A summary that says
components appear first does not establish that the source lacks role
descriptions, inputs, outputs, or relationships. If the available material is
enough for the requested diagnosis, deliver the bounded diagnosis without
ending with requests to paste more material, choose a communication purpose,
or ask for another rewrite.
Respect the source's stated completeness. If the user identifies the supplied
text as the complete draft, do not relabel it as a summary, claim that the
original wording was unavailable, or append a caveat about not having seen the
full document.
Distinguish information that is absent from information that appears too late
or is hard to find. If the source states the business purpose near the end,
diagnose its position; do not say that the document has no purpose or never
explains what the work is for.
When the source already states what each component does, acknowledge those
actions and diagnose only the relationship, order, or decision framing that is
actually absent. Treat an unstated reader task as an observed gap; do not turn
it into a question the user must answer before receiving the diagnosis.
A Diagnose response is incomplete if it stops at problems and risks. Give at
least one prioritized, source-supported revision direction. Moving an existing
business purpose before the component paragraphs is a revision direction, not
an unauthorized full rewrite.
Describe an absent reader task as `文档没有说明读者需要做什么`, not as the
predicted outcome `读者看完不知道如何回应`. If component relationships are
missing, recommend adding them only when another supplied source supports them;
otherwise keep the stated component actions parallel. Do not tell the writer to
infer each component's business contribution from the component description.

Keep predictions about reader cognition or document effects conditional too.
Phrases such as `老板读完仍然不知道`, `读者只会记住`, or `阅读成本会下降`
claim an outcome; use them only when evidence supports that outcome. Otherwise
describe the observable order or omission and the comprehension risk it may
create.

Use the user's requested format and language. When the user writes in Chinese
and gives no contrary direction, write natural Simplified Chinese.

## Set the editing authority

Default to **preserve** for rewrites and drafts based on an existing proposal.
You may change order, headings, wording, explanation, and faithful summaries,
but not budget, schedule, scope, staffing, acceptance, approval state, or the
chosen approach. This includes approved plans: do not redesign one into a pilot
or reopen a decision merely because another option reads better.

Use **propose** only when the user explicitly asks to improve the plan itself or
allows new recommendations. Keep proposed changes visibly separate from source-
supported facts and existing decisions; never write a new suggestion as though
it were already approved.

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
Preserve evidence-bearing status verbs exactly: completing a test is not the
same as passing it, and completing listed tasks does not prove that the overall
project is normal, on schedule, or proceeding as planned. Do not add those
stronger judgments unless the source states them. In a short progress update,
do not add `测试通过`, `功能正常`, `进展正常`, `顺利`, or `按计划推进` merely
because tasks were completed.
Preserve cost conditions as cost conditions: `实时生成需要额外 GPU 预算`
does not say the current version lacks real-time capability, that the phase
excludes it, that the current proposal excludes the budget, that a separate
application is required, or that no budget is needed when it is not enabled.
Before delivery, scan every evaluative or operational clause that was not in
the source. Remove new success labels (`通过`, `正常`, `顺利`, `符合计划`), missing-
field claims, obligations, purposes, or verification steps unless the source
states or necessarily entails them. Mentioning an activity does not authorize
inventing why it is done, how it will be checked, or what later decision it
supports.
Silence is not an explicitly named unknown and does not by itself authorize a
new gap. Surface an absent field only when the user asked for gap analysis or
when the absence directly prevents this reader from completing the current
decision or action; say `材料未说明` rather than upgrading it to `尚未决定`. For
example, if the source already gives a 10-minute acceptance threshold and a
total budget, do not add `材料未提供当前基线`, `费用构成待补`, or similar gaps merely
because those fields are common in project documents.
Plausible but unstated causes, workflows, baselines, owners, decisions, and
boundaries are still unsupported. Merely not contradicting the source is not
evidence; add them only as visibly separate suggestions when **propose** applies.
Completeness means covering the relevant supported material, not filling every
conventional section. A shorter source-bounded draft is more complete than a
polished document whose missing links were supplied by convention.

Keep unknowns at the source's granularity. If the source names budget, schedule,
baseline, and acceptance threshold as unknown, do not unpack them into cost
categories, milestone approvals, trial size, failure handling, owners, module
inputs or outputs, or other “missing information”. You may state the direct
decision dimension an unknown leaves unresolved, such as cost or timing, but do
not turn it into a new prerequisite, approval process, or future decision rule.
A trial and its measurement plan do not by themselves establish whether, when,
or how a later rollout decision will be made.

When the source explicitly names its unknowns, treat that list as closed for
the current draft. For example, `尚无响应基线、负责人和预算` supports marking
only those three gaps; it does not support adding system capability, usage
scope, delivery method, new owner roles, or a “must complete before proceeding”
gate.

## Rebuild for the reader

Before drafting, internally state the core meaning in one sentence: what this
is, what the current situation is, and what this reader most needs to know. The
core may be a question or a progress statement when the evidence does not
support a firm conclusion.

Then use the smallest set of writing actions the task needs:

1. define whether the reader must understand, choose, approve, or act;
2. reorder material around the reader's questions, not the implementation log;
3. explain unfamiliar nouns through source-supported actors and actions before
   retaining terms; when the source gives only components, stay at that level;
4. place each judgment beside the source-supported reason or limitation;
5. preserve important unknowns without manufacturing certainty; and
6. remove repetition and side paths that do not change understanding or action.

When producing versions for different readers, change emphasis, order, and
explanation depth. Do not turn a source activity into a new audit duty, ongoing
confirmation requirement, acceptance purpose, or control process merely
because the execution version needs more detail.

Lead with the bottom line that the reader needs. A decision document normally
lets a scanning reader find the problem, recommendation, strongest reason,
material uncertainty, and requested decision before implementation detail.
Decision-ready does not mean every document needs a new decision. If neither
the request nor the source specifies an approval, owner, pilot, or next-step
process, do not manufacture one from the gaps; explain what the supplied
material supports and keep consequential unknowns visible.

Use an end-to-end scenario only when the supplied sources state or clearly
entail every consequential actor, input, action, review point, output, and
boundary included in it. A list of modules or capabilities is not a workflow.
When the source does not provide the people or sequence, explain the proposal
at the supported component or capability level; do not turn those omissions
into invented steps or new `待确认` items merely to make the scenario look
complete. Include source-supported scope, non-goals, delivery stages,
acceptance, resources, trade-offs, risks, and fallbacks only at the depth this
reader's task needs. Do not force every document into the same headings.

Move implementation detail to an appendix only when it does not change the
decision. A technical constraint stays in the main body when it affects cost,
schedule, feasibility, risk, quality, compliance, or what must be approved.
If the source supplies only decision-changing constraints and no implementation
mechanism, keep the constraints in the body and omit the appendix. Do not invent
placeholder mechanisms, new checks, owners, optionality, or `待补充` appendix
items merely to satisfy an appendix request. Do not pad the explanation with
hypothetical examples of implementation details that the source never supplied.
Omit the appendix cleanly; do not justify its absence by listing conventional
fields such as components, interfaces, or deployment methods that the source
did not mention. When the material supplies only the decision-changing
constraints, deliver those constraints and stop: do not add `来源没有实现细节`,
`没有可放入附录的内容`, or any other explanation for the missing appendix.

When the user requests both a standalone decision entry and a preserved
engineering source, make the short entry self-contained and add an explicit
pointer such as `完整工程方案见文件二` or the supplied attachment name. Merely
placing the full plan later in the same response does not create that pointer.

For substantial decision writing or restructuring, read
[references/decision-documents.md](references/decision-documents.md).

Before every substantive Draft or Rewrite of a decision document, read
[references/source-integrity.md](references/source-integrity.md).
Also read it for multi-source work, conflicting material, or any Diagnose task
where explanation may be mistaken for new fact.

## Make the language clear without hollowing it out

Prefer explicit actors, actions, conditions, and results. Give each paragraph
one job. Replace a technical term when a plain equivalent is accurate; explain
it once when the reader needs the term again; cut it when it serves only the
author. Keep exact numbers, conditions, uncertainty, and the distinction between
`不能` and `尚未`.

A plain-language rewrite must unpack a scope-bearing term, not just move it
into a shorter sentence. For example, explain `已缓存查询` as `能够直接从缓存中
读取结果的查询`, while keeping the sample boundary and the untested write and
cache-miss cases visible.

Do not use abstract words such as “赋能”“闭环”“智能化”“全面提升” as substitutes
for a mechanism, owner, result, or test. Do not infantilize a non-technical
reader or remove precision merely to shorten the document.

For Chinese drafting or sentence-level editing, read
[references/clear-chinese.md](references/clear-chinese.md).

## Deliver a usable document

Default to **clean** delivery for Draft and Rewrite: output only the usable
document. Do not prepend “以下是优化稿”, append a change log, describe your
process, or assert that you preserved every fact. Material unknowns, conflicts,
risks, and missing decisions belong in the document when they affect the
reader's task; they are not process commentary.
Do not expose the mode classification, source inventory, internal decision
analysis, loaded Skill rules, or a justification for the structure. Begin with
the document the user can use.

Use **annotated** delivery only when the user asks to learn from the edit, see
the changes, or review the reasoning. Give the complete document first, then
explain only a few consequential changes with the original wording, revision,
and reason. Diagnose mode still returns diagnosis rather than a silent rewrite.

Do not invent an approval request when the source is only a status update.
Preserve the author's voice when a sample exists; clarity is not permission to
replace it with a generic corporate voice.

Keep a short status update at the source's granularity. A source that says
`本周完成接口联调和本地测试；下周处理监控；当前没有需管理层协调的事项`
supports a complete update with exactly those three facts. It does not support
an added closing judgment such as `进展正常`, `团队按计划推进`, or `整体顺利`, or
an appended caveat such as `尚未给出测试结论`.

## Verify the draft, then test the reader

For a consequential Draft or Rewrite, treat drafting, source review, and any
reader test as one bounded quality workflow. After the first draft, apply the
two-way check in `source-integrity.md` before asking a blind reader to interpret
the document. Use a genuinely independent context for that fact review only
when the capability is available and authorized; otherwise self-check and do
not claim independence.

If a fact or reader check finds a blocking issue, use at most one additional
revision to remove, narrow, or correctly label the unsupported claim, then
rerun the affected checks. A later reader test does not reset this revision
budget. If a blocking conflict or unsupported claim remains, do not call the
document ready; surface the unresolved limitation. Ordinary short, low-stakes
edits do not require an independent review.

For a consequential final document, read
[references/reader-testing.md](references/reader-testing.md). If no independent
reader context is available or authorized, provide the standalone prompt from
that reference without claiming that a test ran. Report first-draft and revised
results separately when the extra revision is used.

Before delivery, confirm that a reader can identify:

- what problem or opportunity matters;
- what is recommended and why;
- what is in and out of scope;
- what evidence is known and what remains unverified;
- what resources, risks, and trade-offs matter;
- what, if anything, they must decide or do next.

Read [references/source-map.md](references/source-map.md) only when maintaining,
auditing, or explaining Write Craft's upstream provenance.
