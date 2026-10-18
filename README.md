# repo-standards · repo-maintainer

**配置一次，以后只提开发需求或反馈，AI 自动完成本轮维护、验证、提交、推送和仓库交付。**

repo-maintainer 是供 AI 编程客户端调用的仓库交付工具。客户端负责理解需求、开发和审查，插件保存项目规则并执行验证及 GitHub 交付。没有开发任务或反馈时不运行巡检。

例如，你只需要说：

> 给列表增加 CSV 导出。

AI 根据项目配置完成开发，更新相关说明、运行检查、修复失败、组织提交、推送并创建 PR；配置为自动合并时，独立审查和 CI 成功后锁定提交合并。测试、CI 和审查反馈继续在同一任务内处理，无需再说“顺便维护、提交、上传”。

## 第一次：让 AI 接入你的项目

本页对应 **1.2.0**，包含项目接入与可恢复的任务交付入口。[1.2.0 发行入口](https://github.com/HaoYangJin/repo-standards/releases/tag/v1.2.0)提供完整插件 ZIP、SHA-256 和安装说明；1.1.0 不含这些新命令。

取得完整源码：

```sh
git clone --branch v1.2.0 https://github.com/HaoYangJin/repo-standards.git
```

在 Codex 或 Claude Code 中打开你要维护的项目，将插件位置交给 AI，并说：

> 请读取 repo-standards/plugins/repo-maintainer/skills/repo-intake/SKILL.md，为当前项目启用自动维护与交付。识别项目规则、测试、CI、默认分支和已有 GitHub 连接，保存配置。以后我只提开发需求或反馈，请自动完成本轮维护与交付。

路径按你实际下载位置提供。AI 会保存项目级入口与配置，保留已有文件；必要时补齐缺失认证或真正无法推断的关键选择。使用插件市场的用户也可加载 v1.2.0 中的完整插件，再提出同样的接入需求，见[插件安装说明](plugins/repo-maintainer/README.md)。

接入会生成：

| 文件 | 用途 |
| --- | --- |
| `AGENTS.md` / `CLAUDE.md` 中的托管段 | 让客户端在后续开发任务中读取交付规则 |
| `.repo-maintainer/config.json` | 保存验证命令、目标分支、CI 和交付策略，不含凭据 |
| `.repo-maintainer/plugin/` | 可随项目复制的完整运行文件，不依赖原下载目录 |

这些文件可随项目提交并共享。任务记录、日志和验证证据放在 Git 元数据内，不进入提交。AI 应确认接入状态完成，再结束首次配置。

## 以后：正常提需求或反馈

- **开发**：“增加 CSV 导出，字段顺序按当前页面。”
- **修复**：“空输入会崩溃，修复这个问题。”
- **反馈**：“这个 PR 的 Windows CI 失败了，处理后继续交付。”
- **缩小范围**：“这次只改本地，不推送。”
- **发布**：“这轮完成后发布 1.2.0。”只有明确的版本发布要求才会执行发行。

配置支持仅本地提交、推送并交付 PR、验证后自动合并。用户本轮更窄限制、项目规则和客户端权限优先。这里的“上传仓库”通常指提交和推送；版本发行按独立的明确请求执行。

新 Issue/评论只有被 AI 客户端带入任务后才处理，本工具不后台监听 GitHub。普通问答与只读审查按原范围执行。

## AI 自动做哪些事

接入项目 → 读取需求/反馈 → 开发与相关维护 → 实际验证 → 独立审查 → 提交/推送/PR → 等待 CI 或修复反馈 → 按策略交付并结束本轮。

一次中断后可读取状态继续，复用已有提交和 PR。相同事件不会重复创建任务；结果不确定的远端写入先查询再决定下一步。缺失权限或无法解决的外部问题会保留进度并说明具体阻塞。

使用 Python 3.11+、Git；GitHub 交付还需要可用的 gh 认证。AI 客户端需要具备执行命令及独立审查的能力。具体接入、命令和恢复方式见[项目工作流](plugins/repo-maintainer/references/project-workflow.md)。实际验证范围见[验收记录](docs/validation.md)。

## 其他能力与资料

核心入口是 repo-intake 和 maintenance-delivery。仓库审查、技能维护、展示和版本发布按本轮目标调用，不要求每次开发都执行全部技能。

- [插件说明与安装](plugins/repo-maintainer/README.md)
- [项目配置、任务与恢复](plugins/repo-maintainer/references/project-workflow.md)
- [可选的仓库展示](docs/showcase.md)
- [60 个仓库的研究资料](research/README.md)：设计参考，不是使用前置条件
- [协作与提交规范](docs/git-workflow.md) · [技能编写规范](skills/skill-authoring/references/authoring-standard.md)
- [贡献说明](CONTRIBUTING.md) · [本插件的发行流程](docs/releases.md)

## 开发本插件

```sh
python -m unittest discover -s tests
python scripts/build_plugin.py --output dist
```

本仓库自身复用 plugins/repo-maintainer 运行目录，避免复制一份插件。普通项目按上面的“一次接入”使用即可。
