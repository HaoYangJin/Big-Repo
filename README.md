# repo-standards

维护 Git 仓库协作、提交说明和 AI 技能编写的中文规范，同时提供可复用模板与技能。

<!-- repo-maintainer:frontpage:start -->

[![Checks](https://github.com/HaoYangJin/repo-standards/actions/workflows/check.yml/badge.svg?event=pull_request)](https://github.com/HaoYangJin/repo-standards/actions/workflows/check.yml)
[![Release](https://img.shields.io/github/v/release/HaoYangJin/repo-standards?label=release)](https://github.com/HaoYangJin/repo-standards/releases)
[![Stars](https://img.shields.io/github/stars/HaoYangJin/repo-standards?style=flat&label=stars)](https://github.com/HaoYangJin/repo-standards/stargazers)

**60 个真实样本 → 6 项维护技能 → 一轮有证据的交付。**

| 拿来用 | 看研究 | 动手体验 |
| --- | --- | --- |
| [下载插件 1.0.0](https://github.com/HaoYangJin/repo-standards/releases/tag/v1.0.0) · [安装说明](plugins/repo-maintainer/README.md) | [分类档案](research/README.md) · [实践对比](research/COMPARISON.md) | [两分钟体验](#两分钟体验) · [六类玩法](plugins/repo-maintainer/skills/repo-showcase/references/showcase-catalog.md) |

徽章读取真实 GitHub 状态：Checks 对应最近的 PR 工作流，不能代替某个提交的验收；正式发行前 Release 可能显示无版本。查看[运行记录](https://github.com/HaoYangJin/repo-standards/actions)或[发行列表](https://github.com/HaoYangJin/repo-standards/releases)可核对实际状态。

<!-- repo-maintainer:frontpage:end -->

## 下载与安装

[1.0.0 发行页](https://github.com/HaoYangJin/repo-standards/releases/tag/v1.0.0)提供插件 ZIP、SHA-256 校验和及安装说明；发布前这些链接尚不可用。GitHub 自动生成的 Source code 是完整研究仓库，插件专用包名为 `repo-maintainer-1.0.0.zip`。

- [下载插件 ZIP](https://github.com/HaoYangJin/repo-standards/releases/download/v1.0.0/repo-maintainer-1.0.0.zip)
- [下载 SHA-256 校验和](https://github.com/HaoYangJin/repo-standards/releases/download/v1.0.0/repo-maintainer-1.0.0.zip.sha256)
- [安装与使用说明](plugins/repo-maintainer/README.md#安装与平台状态)

ZIP 同时包含 Codex 与 Claude Code 清单、六个技能及工具；下载不会自动安装。实际客户端加载状态见[验收报告](docs/validation.md)。

## 两分钟体验

克隆源码后，在仓库根目录执行下面两条只读命令，无须安装第三方 Python 包：

```text
python plugins/repo-maintainer/scripts/repo_tools.py snapshot --repo .
python plugins/repo-maintainer/scripts/repo_tools.py showcase --repo . --public
```

第一条查看工作区与版本指纹，第二条审查首页的链接和素材。展示审查默认离线，外部图表可用性需另行核对。若用于其他仓库，未确认公开性时不要带 `--public`。

<details>
<summary>展开：把这三个玩法直接交给 AI</summary>

- **只读体检**：“使用 repo-audit 和 repo-showcase 审查当前仓库，给出维护与展示建议，不修改文件。”
- **预览展示**：“使用 repo-showcase，为这个公开仓库推荐有真实数据支撑的玩法，先给 README 差异预览。”
- **完整交付**：“使用 maintenance-delivery 优化已确认的问题，按项目规则完成验证、独立审查和 CI，通过后自动合并。”

实际支持范围、首次失败交接与授权边界见插件说明；不会因为复制一句指令就获得仓库权限。

</details>

## 仓库的成长与参与

<!-- repo-maintainer:activity:start -->

### Star History

<a href="https://www.star-history.com/#HaoYangJin/repo-standards&amp;Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HaoYangJin%2Frepo-standards&amp;type=Date&amp;theme=dark">
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HaoYangJin%2Frepo-standards&amp;type=Date">
    <img alt="repo-standards 的 Star History，星标不代表质量或用户人数" src="https://api.star-history.com/svg?repos=HaoYangJin%2Frepo-standards&amp;type=Date" width="800">
  </picture>
</a>

[图表文字入口](https://www.star-history.com/#HaoYangJin/repo-standards&Date) · [GitHub 原始星标记录](https://github.com/HaoYangJin/repo-standards/stargazers) · [提交活动](https://github.com/HaoYangJin/repo-standards/commits/main/) · [版本时间线](https://github.com/HaoYangJin/repo-standards/releases)

图表由 Star History 按公开数据动态提供，更新时间与缓存由服务控制；本仓库不编造趋势。零 Star 或数据不足时可能没有曲线；图表不可用时仍可使用上面的文字入口。不会向该服务发送私有仓库标识或登录凭据。

### 项目故事

| 足迹 | 可以核对的记录 |
| --- | --- |
| 整理提交与技能编写规范 | [Git 工作流](docs/git-workflow.md)与[技能编写规范](skills/skill-authoring/references/authoring-standard.md) |
| 从 60 个样本提炼维护实践，第一次用插件维护自己 | [研究索引](research/README.md)与[已合并 PR #1](https://github.com/HaoYangJin/repo-standards/pull/1) |
| 补足实际加载、模型冒烟与首次发行准备 | [第二轮记录](docs/self-review-round-2.md)与[本轮 PR #2](https://github.com/HaoYangJin/repo-standards/pull/2) |

[参与贡献](CONTRIBUTING.md) · [提出问题](https://github.com/HaoYangJin/repo-standards/issues) · [查看真实贡献者](https://github.com/HaoYangJin/repo-standards/graphs/contributors)

<details>
<summary>一个维护彩蛋：规范本身也需要被验证</summary>

这套插件已经用来维护自己的仓库。每轮记录保留实际问题、测试和限制；如果说明与行为不一致，可以直接提出 Issue，让下一轮维护有明确的起点。

</details>

展示依赖、更新和移除方式见[首页展示维护说明](docs/showcase.md)。

<!-- repo-maintainer:activity:end -->

## 官方仓库研究与维护插件

- [60 个仓库分类档案](research/README.md)：包含真实提交、PR、发布及固定的仓库玩法维度。
- [共性与差异比较](research/COMPARISON.md)：按内容类型归纳，区分候选信号、实际观察与建议。
- [研究方法与限制](research/METHODOLOGY.md)：采样、来源时间、未知项和复现命令。
- [repo-maintainer 插件](plugins/repo-maintainer/README.md)：Codex 优先，兼容 Claude Code，经验证自动合并 PR。
- [验收报告](docs/validation.md)：本机测试、平台验证状态和已知限制。

插件固定覆盖仓库接管、日常维护、审查、发布准备、技能维护和展示玩法。默认首次非预期验证失败即交接，默认在验证与独立审查通过后自动合并，不正式发布或部署；私有仓库不接入公开统计图表。

## 直接让 AI 管理本仓库

无需先安装插件：让当前代理读取仓库内的技能和项目规则即可执行。例如：

> 使用 repo-intake、repo-audit 和 maintenance-delivery，完成一轮审查、修正、验证和复核；通过本地检查、独立审查和 CI 后自动合并，首次非预期失败即保留现场并交接。

本仓库已经完成首版三系统 CI；[第一轮自我优化记录](docs/self-review-round-1.md)记录采用插件维护自身的范围与证据。1.0.0 已补做两端隔离加载，并验证 Codex 真实模型调用展示审查；Claude Code 的模型任务仍未验证。详情见验收报告，不与直接读取技能执行混为一谈。

[第二轮优化与首次发行准备](docs/self-review-round-2.md)记录打包安全修正、下载入口和 1.0.0 的发布范围。

在仓库根目录运行：

```text
python -m unittest discover -s tests
python scripts/build_plugin.py --output dist
```

研究结果、六个技能和六类仓库玩法可分别使用，不需要为小型仓库引入全部流程。

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
git config --local commit.template "/absolute/path/to/repo-standards/templates/commit-message.txt"
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
