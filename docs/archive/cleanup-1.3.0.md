# 1.3.0 发布前清理审计

检查日期：2026-10-19。基准为主线 `46723a1526afb96168983a66dbda0a2865ab0edb`，对应已合并 PR #9。此次审计区分“入口整理”“历史归档”和“删除”，不把尚未删除的分支报告成已清理。

## 文件与文档

基准共有 208 个受跟踪文件，未发现被跟踪的 ZIP、dist/work/tmp 产物、Python 缓存或日志。产物由 .gitignore 排除，发行包仅包含插件运行文件；不把机器上的其他检出当作本仓库文件删除。

本轮把三份 self-review-round 历史记录移到 docs/archive，增加历史索引并修复相对链接；当时的失败、策略与验收结论保留，不改写为当前状态。README 与安装文档去除候选版身份，源码和市场示例固定到 v1.3.0，明确正式发行后使用，避免随 main 漂移。当前展示、安装、目标对照和验收文档保留在 docs 根目录。

以下不是废弃项，继续保留：

- research 的 60 份原始数据与 60 份分析档案：插件规范的可追溯来源，不是运行产物。
- 根目录 skills/templates：原始可复用规范；插件内 skills/templates：维护交付工具，两者用途不同。
- 各技能内 task-protocol 与 project-workflow 副本：支持技能目录独立复制，不合并成越出技能边界的共享引用。
- repo-maintainer 内部 ID、源码与配置目录：兼容已接入项目。Repo-Standards 用于显示与发行包；不是遗漏更名。
- 历史 Release 和版本标签：回退与溯源依据，不覆盖、不移动。

## 分支与未完成工作

发布准备分支创建前，远端有 main 加 9 个工作分支。以下 8 个分支的 HEAD 与对应已合并 PR 的最终 HEAD 一致，无合并后新增提交：

| 分支 | 合并记录 |
| --- | --- |
| feat/repo-maintainer | PR #1 |
| fix/plugin-release-1.0.0 | PR #2 |
| feat/ai-automerge-1.1.0 | PR #4 |
| ci/release-upload-automation | PR #5 |
| fix/release-draft-lookup | PR #6 |
| feat/task-driven-project-workflow | PR #7 |
| release/1.2.0 | PR #8 |
| work | PR #9 |

这些分支已核查，但未删除：仓库 AGENTS.md 明确“不自动删除分支”。Squash 合并不意味着原分支提交成为 main 的祖先，不能仅用 git branch --merged 判断可删性。

另有 `feat/repo-maintainer-1.1.0`，对应仍开放且有冲突的 [PR #3](https://github.com/HaoYangJin/Repo-Standards/pull/3)。该分支包含主线没有的 host-check / distribution 验证脚本与 CI 改动，不可仅因版本号较旧就视为已废弃。保留 PR 和分支，后续应单独评估取舍，不能用本次 1.3.0 发布替它作废或宣称已交付。

本轮 release/1.3.0 是独立发布准备分支，遵循相同审查、CI 与自动合并流程，合并不自动删除分支。

## 结论

已完成当前入口整理、历史记录归档、固定版本安装说明及文件卫生检查。未执行分支删除，未抹去历史研究与验收证据；旧 PR #3 的取舍仍待单独处理。本记录是检查时快照，不代表持续同步的分支状态。正式发行必须另核对已合并提交、固定标签、实际 Release 与下载附件摘要。
