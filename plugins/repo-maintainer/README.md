# Repo-Standards

**给 AI 编程客户端提供项目级的自动维护与仓库交付能力。接入一次，以后只提开发需求或反馈。**

客户端执行开发和推理；插件保存项目策略，管理任务与验证状态，完成推送、PR 和经验证的自动合并。没有任务时不运行定时巡检，也不后台监听 Issue。

本页对应 1.3.0 候选版本。显示名和发行 ZIP 使用 Repo-Standards；机器 ID、源码路径、项目配置目录及技能命令保留 repo-maintainer，以兼容既有安装。Claude Code 等按机器 ID 显示名称的客户端仍可能显示 repo-maintainer，不再使用中文插件名。

## 三步使用

1. **加载完整插件。** 从源码取得 plugins/repo-maintainer，或通过支持的客户端本地插件市场加载。
2. **让 AI 接入项目。** 说：“为当前项目启用 repo-maintainer 自动维护与交付。识别规则、验证与 CI、默认分支和现有 GitHub 连接，保存配置。”AI 使用 repo-intake 检查并运行一次 init，补齐必要信息。
3. **以后正常提需求。** 例如“增加 CSV 导出”“修复空输入崩溃”“CI 失败了，修复后继续”。客户端通过项目说明读取 maintenance-delivery，自动完成本轮维护和交付，无需再次交代提交或上传。

默认写入项目的 AGENTS.md / CLAUDE.md 托管段、.repo-maintainer/config.json 与完整运行目录。已有说明与用户工作保留；不会修改全局客户端配置。配置与运行文件可随仓库共享，任务状态和日志留在 Git 元数据中。

接入状态必须确认完成。验证命令、CI 或远端尚待调查时，AI 继续处理，不把 needs-configuration 当作安装成功。详见[项目工作流](references/project-workflow.md)。

## 安装到客户端

### Codex

在支持插件市场的客户端中登记源码市场并加载 repo-maintainer：

```text
codex plugin marketplace add HaoYangJin/repo-standards --ref main
```

按客户端的插件界面安装并开启新会话。不同版本客户端的命令和加载方式以 [Codex 官方文档](https://developers.openai.com/plugins/build/plugins) 为准。项目接入使用官方 [AGENTS.md 机制](https://developers.openai.com/codex/guides/agents-md)。

也可直接让 AI 读取克隆源码中的 repo-intake/SKILL.md，接入后使用项目内的完整运行目录；无需先更改全局插件设置。

### Claude Code

可临时加载完整插件目录：

```text
claude --plugin-dir /path/to/repo-standards/plugins/repo-maintainer
```

或通过本仓库的 .claude-plugin/marketplace.json 主动安装。项目接入写入官方 [CLAUDE.md 机制](https://code.claude.com/docs/en/memory) 使用的项目说明。参考 [Claude Code 插件文档](https://code.claude.com/docs/en/plugins)。

客户端插件发现、项目说明读取、模型行为和独立审查能力分别验证；过去 1.0.0 的加载记录不能代替新入口的真实客户端验收，详见源仓库 docs/validation.md。

## 配置与日常任务

项目配置保存验证 argv、CI 名称、基准分支和交付终点：

| 终点 | 本轮完成结果 |
| --- | --- |
| commit | 验证、审查后仅本地提交 |
| pr | 推送并创建或更新 PR |
| merge | 本地验证、独立审查和 CI 成功后锁定 head 自动合并 |

用户“只本地”“只审查”等限制优先。发布默认为 explicit-request，只有明确指定版本才执行；日常提交/推送不自动打版本标签。项目规则、平台要求的人工审批和宿主权限继续生效。

AI 调用 project_workflow.py 的 begin → check → review → deliver，使用 status 恢复中断，使用 block 记录外部阻塞。工具保留每轮验证和历史失败，复用已推送提交与已有 PR，实际查询确认交付结果。相同事件不重复交付，同一工作树的任务操作使用进程锁。

这些是 AI 的工具入口，用户不需要手填 task.json 或 evidence.json。命令、字段及恢复细节放在[项目工作流参考](references/project-workflow.md)。完整运行目录需要 Python 3.11+、Git；GitHub 交付使用已认证的 gh，不保存密钥或替客户端登录。

## 按需调用的技能

| 技能 | 何时使用 |
| --- | --- |
| repo-intake | 首次接入或尚未了解项目时 |
| maintenance-delivery | 已接入项目的开发需求和任务反馈 |
| repo-audit | 明确要求审查仓库流程时，默认只读 |
| skill-maintenance | 本轮需要修改 AI 技能时 |
| repo-showcase | 本轮需要维护 README 展示或素材时 |
| release-preparation | 明确要求准备或执行指定版本发布时 |

研究与规范是参考资料，不是普通使用者的必读前提。共享工具 repo_tools.py 的 snapshot/preflight/accept/merge-readiness/showcase/pr 只读，preview 只输出预览，merge 会执行远端合并；项目工作流复用其门槛，不绕过验证、审查或 GitHub 保护。

## 下载、校验与升级

1.3.0 制品名称为 `Repo-Standards-1.3.0.zip`、`Repo-Standards-1.3.0.zip.sha256` 与 `INSTALL-1.3.0.md`；ZIP 顶层目录为 `Repo-Standards/`。实际发行状态查看 [Releases](https://github.com/HaoYangJin/repo-standards/releases)；候选源码和本地构建不表示已公开发行。旧版 [1.2.0](https://github.com/HaoYangJin/repo-standards/releases/tag/v1.2.0) 保留原名称供回退。

校验后完整解压，在客户端加载解压后的 `Repo-Standards` 目录（其中包含隐藏清单目录、skills、scripts 和 assets），不要按旧的 ZIP 顶层路径加载：

```sh
sha256sum -c Repo-Standards-1.3.0.zip.sha256
claude --plugin-dir /path/to/Repo-Standards
```

macOS 使用 `shasum -a 256 -c`；PowerShell 使用 `Get-FileHash -Algorithm SHA256` 与校验文件比较。升级在新目录准备完整版本，保留项目配置和用户改动；由 AI 核对后更新已接入项目的完整运行目录，不混合覆盖单个文件。现有 `.repo-maintainer/config.json`、任务记录和技能名称无需迁移；回退同样替换完整运行目录。

## 离线探索台与交付演练

在解压后的插件目录运行（Python 3.11+；真实快照另需 Git）：

```sh
python scripts/explore.py --demo --output ../Repo-Standards-demo.html
python scripts/explore.py --repo /path/to/project --output ../Repo-Standards-report.html
```

用浏览器打开输出 HTML。页面含真实结构信号或明确标记的示例数据、四种交付演练、六类玩法筛选和快照导出；无外部依赖和请求。输出路径必须尚不存在。快照不是实时监控；存在测试或 CI 文件不代表它们通过。模拟失败、修复与合并只改变页面状态，不写入真实验证证据，也不执行 Git 或 GitHub 操作。

不读取源文件内容、远端地址或任务日志。报告包含仓库名、分支名和提交标识，分享前核对；删除输出 HTML 即可移除，无需关闭服务。只复制技能目录的用户按技能内参考说明操作，探索台需要完整插件。

repo-standards 的 GitHub Actions 发布流程用于这个插件自身发行。目标项目的版本发布按其实际构建、凭据和发布规则执行，不自动复制本仓库的发布工作流。
