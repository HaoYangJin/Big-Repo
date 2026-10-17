# repo-standards

维护 Git 仓库协作、提交说明和 AI 技能编写的中文规范，同时提供可复用模板与技能。

## 官方仓库研究与维护插件

- [60 个仓库分类档案](research/README.md)：包含真实提交、PR、发布及固定的仓库玩法维度。
- [共性与差异比较](research/COMPARISON.md)：按内容类型归纳，区分候选信号、实际观察与建议。
- [研究方法与限制](research/METHODOLOGY.md)：采样、来源时间、未知项和复现命令。
- [repo-maintainer 插件](plugins/repo-maintainer/README.md)：Codex 优先，兼容 Claude Code，维护到可审查 PR。
- [验收报告](docs/validation.md)：本机测试、平台验证状态和已知限制。

插件固定覆盖仓库接管、日常维护、审查、发布准备、技能维护和展示玩法。默认首次非预期验证失败即交接，不自动合并、发布或部署；私有仓库不接入公开统计图表。

## 阅读入口

- [Git 工作流](docs/git-workflow.md)：分支、暂存、验证、推送与 PR。
- [提交规范](skills/git-commit/references/commit-conventions.md)：提交类型和说明示例。
- [技能编写规范](skills/skill-authoring/references/authoring-standard.md)：触发条件、目录、授权边界与验收。
- [贡献说明](CONTRIBUTING.md)：修改这些规范的方法。

## 使用方式

规范可以直接阅读，也可以按目标项目的需要复制模板。本仓库的约定只适用于本仓库；其他项目采用前应检查已有规则。

### 提交模板

在需要使用模板的仓库内执行，将路径替换为本仓库的实际位置：

```powershell
git config --local commit.template "D:/Code/Github/Repo/templates/commit-message.txt"
git commit
```

此设置只影响当前仓库；使用 `git commit -m` 时不会打开模板。

### 可复用技能

| 技能 | 用途 | 入口 |
| --- | --- | --- |
| git-commit | 检查改动范围、组织提交并提供验证结果 | [SKILL.md](skills/git-commit/SKILL.md) |
| skill-authoring | 创建、改进和验收任务型技能 | [SKILL.md](skills/skill-authoring/SKILL.md) |

把需要的技能**整个目录**复制到所用代理支持的技能目录，保留其中的 `references/`。安装位置和发现机制取决于具体工具，本仓库不自动安装技能或修改全局配置。

[技能草稿模板](templates/SKILL.md.template)仅供起草，完成替换并命名为 `SKILL.md` 后再使用。

## 文件约定

文本采用 UTF-8、LF 换行。规范调整应解释适用范围，避免把一个项目的特殊情况写成通用要求。PR 配置了 Windows、macOS、Linux 离线测试矩阵；未配置自动提交钩子或分支保护，也不自动安装插件。

## 参考来源

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [Agent Skills 格式规范](https://agentskills.io/specification)

上述来源用于格式依据；本仓库的工作流与示例属于本地约定。
