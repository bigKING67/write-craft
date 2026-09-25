# Decision documents

Use this reference when a draft must help a non-technical reader understand a
complex proposal, compare options, approve a bounded next step, or decide not
to proceed. It is guidance, not a mandatory template.

## Contents

- Start from the decision
- Find the load-bearing idea
- Design the first reading layer
- Separate decision and engineering layers
- Use scenarios, sections, and tables deliberately
- Keep evidence and constraints visible
- Learn from complete examples

## Start from the decision

State the reader's task in one sentence. Distinguish these common outcomes:

- **Understand:** establish a shared model; do not invent an approval request.
- **Choose:** compare real alternatives using the same decision criteria.
- **Approve:** state the bounded resource, scope, risk, or next stage being
  authorized.
- **Act:** name the owner, next step, and trigger or deadline when supplied.

“Learn about the project” is not yet a decision. When no decision is required,
the document may end with a next step already supplied by the source; otherwise
it does not need to manufacture one.

## Find the load-bearing idea

Identify the one idea that makes the rest easier to understand. Express it in
plain language without losing its condition or uncertainty. Use it to organize
the explanation; do not give every implementation detail equal weight.

For a technical-to-business rewrite, translate this sequence:

`implementation mechanism -> changed workflow -> observable result -> decision value`

Use only the links the source states or clearly entails. A component list may
support a component-level explanation without supporting a changed workflow.
Do not skip directly from a mechanism to revenue, efficiency, quality, or
adoption unless evidence establishes that link, and do not fill an absent link
with a conventional process.

## Design the first reading layer

A reader should be able to find the source-supported items relevant to this
task near the beginning. These often include:

1. the current problem or opportunity;
2. the recommendation or current conclusion;
3. why this option is preferred now;
4. the most important limitation or uncertainty;
5. the decision or next action, if one exists.

Write the summary after the body is sound, even though it appears first. A
summary is not a teaser: it should contain the conclusion.

## Separate the decision entry from the engineering source when needed

When one document must serve both decision-makers and implementers, a short
summary at the top may still leave the first reading path too long. If the
existing engineering plan must remain complete, preserve it as the detailed
source and create a shorter decision entry that can stand on its own. The short
entry should contain only the supported elements needed for the decision. These
may include the recommendation, a representative workflow when the source
provides one, a bounded first-stage deliverable and acceptance method, explicit
non-goals, material unknowns, and a real next decision or action. Omit an
inapplicable element instead of filling it from convention. Link to the detailed
source for architecture and implementation mechanics instead of copying them
all.

If the short entry and engineering source are separate files, or may be split
after delivery, put an explicit pointer inside the short entry itself. Name the
included file, attachment, or exact section, for example `完整工程方案见文件二`.
Showing the engineering source later in the same response is not enough: the
short entry must retain the path when copied or sent on its own.

Do not use the split to hide a constraint. Any fact that changes feasibility,
cost, timing, risk, acceptance, or the requested authorization must still
appear in the decision entry.

## Use a source-supported scenario

When an architecture description is too abstract and the source supplies the
necessary relationships, show one representative flow:

1. who begins the task and with what input;
2. what the proposed system or process does;
3. where a human reviews, changes, or rejects the result;
4. what output is produced;
5. how success and failure will be observed.

Label the scenario as an example when it is illustrative. Do not let an example
silently become a promise that every case behaves the same way. Each actor,
input, action, review point, output, and boundary must come from the source or a
clear entailment. Module names alone do not establish who initiates work, where
humans intervene, what gets recorded, or what happens next. If those links are
absent, explain the components without constructing a scenario.

## Layer the body by reader need

Choose only the sections the decision requires and the source can support.
Useful candidates include:

- current problem and why it matters now;
- proposal and representative use case;
- first-stage scope and explicit non-goals;
- alternatives and trade-offs, including the status quo when relevant;
- deliverables, owners, dependencies, and sequence;
- acceptance method and evidence needed;
- people, time, budget, and operational load;
- risks, mitigations, stop conditions, and fallback;
- requested decision or next action;
- technical appendix.

Use consistent criteria when comparing options. Do not praise one option for
speed and reject another for cost without showing both criteria for both
options.

## Use the lightest table that fits the reader's task

For a small, static comparison such as scope, stages, responsibilities, or
acceptance criteria, use the destination document's native table when it makes
scanning easier. Introduce a spreadsheet or another embedded data artifact only
when the task actually needs formulas, live data, filtering, calculation, or
independent data collaboration. A more powerful container is not automatically
a clearer one; it can add navigation, access, and maintenance overhead without
helping the decision.

## Keep decision-changing constraints visible

A technical fact belongs in the main body when it changes any of these:

- feasibility or supported use cases;
- cost, staffing, or operational burden;
- delivery time or dependencies;
- security, privacy, compliance, or rights;
- failure recovery or business continuity;
- acceptance thresholds or quality risk.

Explain the consequence in reader language, then place implementation mechanics
in the appendix if further detail is useful.

## Keep the evidence boundary explicit

Use the strongest accurate verb:

- **observed / verified:** directly supported by current evidence;
- **estimated:** derived from stated inputs or a model;
- **expected:** a reasoned forecast, not yet observed;
- **targeted:** an intended outcome;
- **unknown / pending confirmation:** no adequate basis yet.

If cost, duration, headcount, baseline, or success threshold is missing, retain
`待确认` and state the direct decision dimension it leaves unresolved. Keep the
gap at the source's granularity: do not expand “预算待确认” into conventional
cost categories, or “验收阈值待确认” into trial size, failure handling, owners,
and approval steps. Smooth prose must not conceal the gap or manufacture the
process for closing it.

## Learn from complete synthetic examples

Examples demonstrate decisions and information order, not mandatory wording or
headings. The following material is synthetic and does not describe a real
project state.

**Source material**

> 拟建设设备巡检辅助工具。现场人员提交传感器读数、巡检照片和设备编号；系统标记异常记录并生成检查清单。设备工程师复核清单后决定是否安排检修。本轮不自动停机，也不自动下发维修指令。目标是减少人工筛查巡检记录所需的时间，尚未用同批记录比较实际耗时。预算与验收阈值未确定。本文先解释方案，不申请审批。

**Request**

> 给不了解技术的业务负责人说明方案。只改表达，不改变范围，也不申请立项。

**Usable rewrite**

> ## 从巡检记录生成异常检查清单：设备巡检辅助方案说明
>
> 这套拟建设的工具，负责从现场提交的巡检记录中标记异常，并生成一份检查清单，再交给设备工程师复核。它不会自动停机，也不会直接下发维修指令。
>
> 实际使用时，现场人员提交传感器读数、巡检照片和设备编号，系统据此标记异常记录并整理检查清单。设备工程师复核后，再决定是否安排检修。
>
> 方案希望减少人工筛查巡检记录的时间，但目前还没有用同一批记录比较实际耗时，因此不能把节省时间写成已经验证的效果。预算和验收阈值也尚未确定。
>
> 本文用于说明方案，当前不提交审批请求。

The first paragraph establishes the proposed state and boundary. The second
turns implementation nouns into a workflow. The third keeps the target beside
the evidence gap. The last sentence preserves the communication purpose instead
of manufacturing an approval request.

### When the source contains components but no workflow

**Source material**

> 这是一套库存盘点辅助方案。现有材料只列出图像识别、货品匹配、规则调度和报表生成四个组成部分，没有说明具体输入、输出、先后关系、人工节点、投产状态或报表形态。预算、工期、现状基线和验收阈值尚未确定。本文只说明方案，不申请审批。

**Request**

> 写成业务负责人能直接理解的方案说明，不改变范围。

**Usable rewrite**

> ## 库存盘点辅助方案说明
>
> 现有材料把方案分为图像识别、货品匹配、规则调度和报表生成四个部分。当前只能确认这四项构成，不能据此判断它们怎样衔接、哪里需要人工确认，或最终会形成什么报表。
>
> 预算、工期、现状基线和验收阈值尚未确定，因此目前还不能判断成本、交付时间和实际效果。本文只说明方案，不申请审批。

This version does not convert the four names into a guessed process or unpack
the stated unknowns into a longer diligence list. Sparse source material calls
for a short, bounded explanation, not a conventionally complete proposal.

### When the source is already sufficient for approval

**Source material**

> 当前首次审阅时长中位数为 28 分钟，采购专员需要在多个条款库之间查找内容。建议用六周为 30 名采购专员试运行合同条款提示功能。系统只提示可能需要关注的条款，由采购专员确认后处理，不自动修改或提交合同。投入为法务 1 人、采购主管 1 人、工程师 2 人，预算上限 20 万元。试运行前后比较首次审阅时长、人工修改率和漏检数；通过条件为首次审阅时长中位数不高于 15 分钟、没有未经采购专员确认的合同提交。主要风险是条款库过期和权限配置错误，分别由法务每周复核、工程师上线前检查。请管理层批准六周范围和 20 万元预算。

**Request**

> 按材料直接改写成审批稿，已有信息不要再问。

**Usable rewrite**

> ## 合同条款提示功能试运行申请
>
> **申请批准：**用六周时间面向 30 名采购专员试运行合同条款提示功能，预算上限 20 万元。
>
> 现有材料记录了两项现状：首次审阅时长中位数为 28 分钟；采购专员需要在多个条款库之间查找内容。材料没有证明跨库查找导致了 28 分钟的审阅时长，因此这里只并列说明，不作归因。
>
> 系统只提示可能需要关注的条款，由采购专员确认后处理，不自动修改或提交合同。参与人员为法务 1 人、采购主管 1 人、工程师 2 人。
>
> 试运行前后比较首次审阅时长、人工修改率和漏检数。明确的通过条件有两项：首次审阅时长中位数不高于 15 分钟；没有未经采购专员确认的合同提交。材料没有把人工修改率和漏检数列为通过条件。
>
> 条款库过期由法务每周复核，权限配置错误由工程师在上线前检查。本次只申请批准上述六周试运行范围和 20 万元预算。

The rewrite uses the supplied approval facts without reopening whether the
budget contains particular cost categories, inventing thresholds for the other
comparison metrics, or adding a later rollout decision. It also prevents two
adjacent observations from becoming an unsupported causal claim. When the
source is sufficient, completeness means organizing what is there and stopping.

For an approved plan, the same method improves explanation without reopening
scope. For a request that explicitly permits plan changes, put new suggestions
in a separate proposal section and label their effect on the approved baseline.
