# Write Craft

Write Craft 把复杂技术方案、项目提案和工程说明重组为非技术决策者能够理解、判断并采取行动的文档。它优先解决信息顺序、论证边界和读者理解，而不是只把句子润色得更顺。

## V0.2 能力

- 改写已有工程方案：完整阅读原稿后，先给可用的老板版或决策版全文。
- 从材料起草决策文档：明确问题、建议、依据、取舍、投入、风险和待决事项。
- 只做诊断：指出结构、论证、术语和证据问题，不擅自改写全文。
- 保留精度：不编造预算、工期、人员、效率、收益、指标或已实现能力。
- 独立读者测试：在有独立上下文且获授权时执行，否则交付可复制的测试提示词。

V0.2 不负责广告创意、产品 UI 微文案、飞书或 Word 的平台操作，也不替代面向开发者的 API/运维文档 Skill。需要文件或平台操作时，可将 Write Craft 作为内容层与相应能力组合。

## 安装与加载

Pi 可以从本地源码加载，也可以安装固定的 Git 提交或标签：

```bash
# 开发或评测：直接加载当前源码，不修改 Pi 的安装设置
pi --no-skills --skill skills/write-craft

# 日常使用：将 <ref> 替换为经过验证的提交 SHA 或标签
pi install git:github.com/bigKING67/write-craft@<ref>
```

要给同时读取 Agent Skills 目录的宿主使用，可将 `skills/write-craft/`
安装为 `~/.agents/skills/write-craft/`。源码目录、全局安装目录和当前会话
是三个不同状态：文件一致只证明安装内容一致，不证明已经运行的会话加载了
这个版本。升级后应新开会话或按宿主机制重新加载。

## 获取源码

仓库使用 Git submodule 固定上游参考版本。完整克隆源码时使用：

```bash
git clone --recurse-submodules https://github.com/bigKING67/write-craft.git
cd write-craft
```

只使用已打包的 `skills/write-craft/` 不需要加载上游仓库。

## 源码结构

- `skills/write-craft/`：唯一可安装产品。
- `upstreams/`：固定提交的原始参考仓库，不进入安装包。
- `docs/upstream-absorption.md`：吸收、拒绝和延期矩阵。
- `evals/cases.json`：行为验收案例，不包含模型生成结果。
- `scripts/` 与 `tests/`：源码、上游和打包验证。

## 本地验证

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/package_check.py
```

`python3 scripts/upstream_status.py --remote --json` 可只读比较固定提交与远端 HEAD；它不会更新 submodule。

## 真实行为评测

真实评测通过 Pi 显式加载仓库里的 Skill。生成阶段只开放 `read`，用于读取
`SKILL.md` 引用的运行时参考；独立评审阶段不开放工具或 Skill。模型调用不会
在 CI 中自动运行，也不会自动重试。

```bash
python3 scripts/eval_behavior.py \
  --suite smoke \
  --model anthropic/claude-sonnet-4-6 \
  --judge-model anthropic/claude-sonnet-4-6 \
  --thinking medium \
  --judge-thinking high
```

`--suite smoke` 运行四个核心案例；`--suite full` 运行全部案例；重复
`--case <id>` 可以只选择特定案例。结果默认写入被 Git 忽略的
`.artifacts/write-craft-evals/<timestamp>/`，其中包含输入摘要、候选稿、逐项
判分、模型与 Pi 版本、Skill 摘要和退出状态。当前执行器按 Pi `0.80.6`
的 JSONL 事件格式验证；这表示已验证版本，不声明为最低兼容版本。当前基线
使用同一个 Sonnet 4.6 模型的两个独立上下文完成生成与评审，因此可证明上下文
隔离，但不能宣称跨模型复核。

如果生成已经完成、只有评审协议或评审服务失败，可显式使用
`--rejudge <case-artifact-dir>` 重新评审现有候选稿。重新评审写入新的
`rejudge-N/` 目录并保留原失败记录；评测器不会自动重试或覆盖历史。
