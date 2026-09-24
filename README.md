# Write Craft

Write Craft 把复杂技术方案、项目提案和工程说明重组为非技术决策者能够理解、判断并采取行动的文档。它优先解决信息顺序、论证边界和读者理解，而不是只把句子润色得更顺。

## V0.1 能力

- 改写已有工程方案：完整阅读原稿后，先给可用的老板版或决策版全文。
- 从材料起草决策文档：明确问题、建议、依据、取舍、投入、风险和待决事项。
- 只做诊断：指出结构、论证、术语和证据问题，不擅自改写全文。
- 保留精度：不编造预算、工期、人员、效率、收益、指标或已实现能力。
- 独立读者测试：在有独立上下文且获授权时执行，否则交付可复制的测试提示词。

V0.1 不负责广告创意、产品 UI 微文案、飞书或 Word 的平台操作，也不替代面向开发者的 API/运维文档 Skill。需要文件或平台操作时，可将 Write Craft 作为内容层与相应能力组合。

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
