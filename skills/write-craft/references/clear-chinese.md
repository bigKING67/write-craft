# Clear Chinese

Use this reference for Simplified Chinese drafting and editing. The goal is
natural, professional writing that a capable non-specialist can understand on
the first reading without losing precision.

## Give each unit one job

- A heading should carry a finding, boundary, or question when that helps a
  scanning reader; avoid empty labels such as “项目背景” when a meaningful
  statement is available.
- A paragraph should develop one topic. Split it when the actor, time, claim, or
  reasoning step changes.
- A sentence should make the main relationship visible. Long sentences are
  acceptable when one idea requires qualification; they fail when several
  claims compete for attention.

Before polishing sentences, write one private core sentence: “这是什么／现在到
哪一步／这次读者最需要知道什么”. It is a compass, not a required opening.
When evidence does not support a conclusion, the core can be a question,
boundary, or progress statement instead of a confident claim.

## Put actors and actions back into the sentence

Prefer “运营人员提交需求，剪辑人员审核初稿” to “实现需求提交与初稿审核闭环”.
Name the actor when ownership matters. Passive or subjectless Chinese is valid,
but it should not hide responsibility, failure, or the next action.

Turn noun piles into actions:

- “进行方案可行性的验证” -> “验证方案是否可行”
- “完成对素材的检索与筛选” -> “检索并筛选素材”
- “实现效率层面的全面提升” -> state whose time changes, in which step, and
  how it will be measured; otherwise mark it as an unverified goal.

Do not inflate a short update. “已完成接口联调和本地测试；下周补监控，目前
没有需要管理层协调的事项” is clearer than expanding three facts into a project
proposal. `完成本地测试` still does not mean `测试通过` or `已经上线`.

## Keep judgments beside their basis

Place a conclusion next to the source-supported reason, condition, or evidence
gap that qualifies it. For example: “方案值得继续比较，因为它复用现有素材；
但尚无同批耗时对照，暂不能确认效率收益。” Do not add a reason merely to make
the paragraph feel complete. If the source gives only a goal, call it a goal.

## Treat jargon deliberately

For every term unfamiliar to the reader, choose one action:

- **Replace:** use an accurate ordinary phrase when nothing is lost.
- **Teach:** name the term once, explain what it does in this situation, then
  reuse it consistently.
- **Cut:** remove detail that does not help this reader understand or decide.

Do not replace a precise term with a vague benefit word. If the reader will
meet the term in later discussions, withholding its name makes the document
less useful.

A plain-language rewrite must explain a term, not merely move it into a shorter
sentence. For example, `120 个已缓存查询样本` can become `120 条能够直接从缓存中
读取结果的查询`; keep the sample boundary and do not generalize that result to
uncached queries, writes, or the whole system.

## Preserve qualifications

Do not delete or silently strengthen:

- numbers, populations, time windows, preconditions, and exceptions;
- the source and date of evidence when freshness matters;
- uncertainty or competing explanations;
- the distinction between “不能”“暂不支持”“尚未验证”“计划实现”;
- constraints that change cost, time, risk, or the decision.

Use “预计”“目标”“假设”“待验证” only when those are the true evidence states.
Avoid decorative hedging; uncertainty should be specific enough to act on.

## Keep the whole answer within a hard length limit

When the user gives an exact limit, apply it to every user-visible part unless
the user explicitly narrows the limit to a named section. Titles, headings,
table-cell text, appendices, notes, caveats, explanations of changes, and
follow-up items all consume the same budget. Do not call a section “正文” and
then place overflow below it.

Count conservatively and leave margin instead of drafting to the exact edge.
Shorten headings, remove repeated conclusions, flatten low-value structure,
and combine compatible qualifications before removing a fact that changes the
decision. If the requested limit cannot contain the recommendation plus its
material evidence, constraints, and risk, make that trade-off explicit rather
than silently exceeding the limit or deleting the boundary.

## Remove abstract filler

Words such as “赋能”“抓手”“闭环”“智能化”“全链路”“全面提升” are not forbidden,
but each must do more than signal importance. Replace it with the mechanism,
owner, observable result, or test when possible.

Do not add symmetrical slogans, repeated conclusions, unnecessary quotation
marks, or mechanical “首先、其次、最后” transitions merely to sound polished.
Vary sentence rhythm only after the logic is clear.

## Keep the author's voice

When examples of the author's writing exist, preserve their level of warmth,
directness, and formality. Correct ambiguity and stiffness without turning every
document into ceremonial corporate prose. Read the final draft aloud; revise
places that require backtracking or sound unlike something a person would say.
