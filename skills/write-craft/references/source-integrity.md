# Source integrity

Use this reference when a rewrite depends on multiple sources, consequential
facts, ambiguous evidence, or an explanation that could be mistaken for a new
claim. The aim is faithful transformation, not literal copying.

Plausibility is not provenance. A cause, workflow step, baseline state, owner,
decision, boundary, or reader behavior remains unsupported when the source does
not state or entail it, even if it sounds normal and does not contradict the
source. Mark a user-authorized proposal as a proposal; otherwise omit it or
preserve the actual unknown.

Source-bounded writing does not need to look conventionally complete. Before
turning components into a process, identify source support for every actor,
input, action, review point, output, and boundary. If the source provides only
component or capability names, describe only those components or capabilities.
Do not create a workflow, baseline, owner, or `待确认` item to fill the missing
shape of a familiar proposal.

## Allow useful transformation

These changes are normally valid when they preserve meaning:

- explain a term through source-supported actions by a person or system;
- summarize several stated steps as one bounded workflow;
- group related facts and reorder them for the reader;
- state the supported topic or purpose more directly; and
- remove repetition that carries no additional condition or exception.

For example, if the source says the system retrieves clips, arranges them on a
timeline, and renders the result, “生成视频初稿” can be a faithful summary.
“每天自动生产一百条高转化视频” adds unsupported capacity, automation, and
outcome claims.

## Check in both directions

Before delivery, check both directions:

- **Draft to source:** every statement that changes understanding or a decision
  has support, is clearly marked as a proposal, or is explicitly unknown.
- **Source to draft:** every source fact, condition, exception, and decision that
  matters to this reader's task remains visible.

Run this check across the title, summary, tables, captions, body, appendix, and
next-step language. A correct body does not repair a misleading title.

## Protect meaning, not just nouns and numbers

Reject transformations such as:

| Source meaning | Distorted rewrite |
| --- | --- |
| completed testing | testing passed |
| completed listed tasks | overall progress is normal or on schedule |
| production status not stated | never tested in production |
| requires additional budget | guaranteed if funded |
| aims to reduce manual time | has reduced manual time |
| some samples improved | all tasks improved |
| budget is proposed | budget is approved |
| human review remains now | can never be automated |
| real-time use requires more investment | phase one excludes real-time use |
| two metrics changed together | one metric caused the other |

Also preserve modality and time: `cannot`, `not yet supported`, `not yet
verified`, `planned`, and `approved` are different states.

Do not turn a current, phase-specific, or approved boundary into a permanent
commitment. `当前/本期必须人工确认` does not support `永久如此`, `不是过渡做法`,
or `以后也不会自动化` unless the source states that time scope.

## Keep only relevant unknowns visible

Do not turn every absent field into a `待确认` section. Ask whether the missing
fact prevents this reader from understanding, deciding, approving, or acting in
this task. A short progress update may not need a budget; a funding request
usually does. Preserve a relevant gap without inventing a value, owner, reason,
or deadline.

Preserve the granularity of the source. “预算尚未确定” supports saying that cost
cannot yet be assessed; it does not support inventing a required breakdown by
people, compute, and procurement. “验收阈值尚未确定” does not establish a trial
size, failure policy, approval step, or responsible owner. Likewise, a stated
trial and a set of comparison metrics do not entail a later rollout, stop/go
decision, or rule for that decision. Do not disguise these additions as
explanations of why the original gap matters.

Missing information can limit a decision without proving that approval is
impossible or that the gap must be filled before any action. Use the narrowest
supported consequence unless the request or source defines the approval gate.

## Diagnose what is actually present

A diagnosis must preserve facts that the source already explains. Do not call a
component unexplained merely because its relationship to other components is
missing.
Likewise, a business purpose that appears late is not absent. Diagnose the
placement or prominence of information without claiming the document never
states it.
Also preserve what the user says about source completeness. Complete supplied
text must not be downgraded to a summary or accompanied by an invented caveat
that the original wording or full document was unavailable.

**Source excerpt**

> 识别服务读取质检照片并标记异常区域。索引库保存设备编号和照片位置。任务队列记录每条检查任务的处理状态。查询接口按设备编号返回检查结果。我们希望借此减少人工查找异常照片的时间。原稿没有说明需要负责人批准什么。

**Request**

> 只诊断为什么负责人可能难抓住重点，不要重写。

**Bounded diagnosis**

> 影响理解最大的不是四个组件“没有解释”，而是信息顺序和组件关系没有建立。
>
> - **业务目的出现得晚。** 原稿先连续说明四个组件各自做什么，最后才说明希望减少人工查找异常照片的时间。这种顺序可能让读者更难在接触组件时判断这些信息为何重要。可以把原稿已有的业务目的前移，再保留必要的组件说明。
> - **组件动作已有，但关系未说明。** 原稿已经说明识别服务、索引库、任务队列和查询接口分别做什么；没有说明的是它们之间的先后、依赖或数据流。若原材料能支持这些关系，可以补充；如果不能，就保持并列说明，不要补造流程。
> - **阅读任务没有交代。** 原稿明确没有说明负责人需要批准、选择或配合什么。诊断可以指出这一空缺，但不能替作者制造审批事项。

This diagnosis acknowledges the supplied actions, limits criticism to the late
purpose, missing relationships, and absent reader task, and ends without asking
for more material or offering a rewrite service.

## Handle multiple sources and conflicts

Keep source identity and version distinct. A later date or a filename such as
“最终版” does not by itself prove authority. Apply a correction only when the
user, approval record, or explicit version relationship supports it. Otherwise
state the conflict and its decision impact instead of choosing the more
optimistic, convenient, or detailed claim.

When traceability is required, cite the real supplied source location. Do not
invent line numbers, quotes, hashes, or provenance. A valid quote proves where
text came from; it does not by itself prove that the interpretation is correct.
