# Reader testing

Reader testing checks whether the final document works without the author's
conversation history. It is not a confidence ritual and must not be claimed
unless a genuinely fresh context received only the final document and test
questions.

## Prepare the questions

Choose five to eight questions a real reader would ask. Cover the document's
purpose, recommendation, evidence, scope, resources, risks, uncertainty, and
requested action. Use questions that have objectively checkable answers in the
document; do not ask whether the prose “feels good”.

Examples:

- What problem is this proposal trying to solve now?
- What is recommended for the first stage, and what is explicitly excluded?
- What evidence supports the recommendation?
- Which benefits are observed, estimated, targeted, or still unverified?
- What people, time, budget, or dependencies are required or still unknown?
- What could make the proposal fail or cause the team to stop?
- What decision or action is requested from the reader?

## Run when an independent context is available

Give the reader only the final document and questions. Ask it to answer each
question, cite the section that supports the answer, list ambiguities, identify
assumed background knowledge, and flag contradictions. Do not include the
author's intent, prior discussion, expected answers, or suspected defects.

Fix the document, not the test, when the reader cannot answer a material
question. Stop when the questions are answered accurately and a new pass finds
no material ambiguity or contradiction. Do not polish indefinitely for minor
stylistic preferences.

## Fallback prompt

When no independent context is available or authorized, provide this prompt for
a new conversation without claiming the test was executed:

```text
你是一名没有参与该项目、不了解此前讨论的独立读者。只根据下面的最终文档回答问题；不要用常识补齐文档没有提供的信息。

请先回答我附上的每个问题，并为每个答案指出文档中的依据。然后单独列出：
1. 无法从文档回答的问题；
2. 含义不明确或可能有两种解释的表述；
3. 文档默认读者已经知道、但没有解释的背景；
4. 前后矛盾、把目标写成结果或把假设写成事实的地方；
5. 读者可能因此做出错误决定的遗漏。

如果文档没有给出答案，请明确写“文档未说明”，不要猜测。

【待测试文档】
<粘贴最终文档>

【读者问题】
<粘贴 5 至 8 个问题>
```
