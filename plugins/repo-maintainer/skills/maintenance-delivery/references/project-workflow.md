# 配置一次，按开发任务与反馈自动交付

这是完整插件的项目工作流。它由当前 AI 客户端执行，不启动后台代理或定时任务。只复制技能目录时，按 task-protocol.md 手工记录和核对任务；要使用以下命令，应保留完整插件目录及 scripts/。

## 首次接入：交给 AI 完成

用户在目标项目的 AI 会话中说：

> 为当前项目启用 repo-maintainer 自动维护与交付。请识别项目规则、实际测试与 CI、默认分支和已有 GitHub 连接，保存配置。以后我提出开发需求或反馈时，自动完成本轮维护、验证、审查与交付。

AI 先读取项目规则和已有工作，再调用插件 scripts/project_workflow.py 的 init。没有全局插件安装时，也可从克隆的 repo-standards/plugins/repo-maintainer 目录读取 repo-intake/SKILL.md 后执行。目标必须是 Git 仓库根目录；已有用户文件应保留。

init 为 Codex 写入 AGENTS.md 的托管段，为 Claude Code 写入 CLAUDE.md 的托管段，保存 `.repo-maintainer/config.json`，并把完整插件复制到 `.repo-maintainer/plugin/`。这些项目文件可随仓库提交，共享给后续客户端会话和协作者，不依赖原下载目录。已有配置默认保留；`init --update` 只在有明确配置变更需要时使用，不静默升级已复制的运行文件。

在本插件源码仓库内接入时，可加 `--plugin-path plugins/repo-maintainer` 复用现有运行文件，避免复制自身。路径保持仓库相对形式。

## AI 如何补齐配置

配置包含目标仓库、基准分支、验证 argv、真实 CI 名称、交付终点和 explicit-request 发布策略，不含账号、令牌或机器绝对路径。

```text
python scripts/project_workflow.py init --repo /path/to/project --client both --delivery merge --base-branch main --check "npm run test" --ci-check "test"
```

上例仅演示字段，实际命令与 CI 名称应由 AI 从目标项目确认。已有 package.json 的 lint/typecheck/test 和直接使用 unittest.TestCase 的 tests 目录可给出初始建议；其他项目由 AI 检查项目文档、清单和 CI 后用 --check 提供命令。每个 --check 按 argv 执行，不经 shell；需要复合命令时调用项目自己的脚本。

交付终点为 commit（仅本地提交）、pr（推送并交付 PR）、merge（验证后自动合并），默认 merge。用户本轮更窄限制优先。提交本身仍由 AI 按项目语义精确暂存和组织，不使用 git add --all 吞入无关工作。

merge 模式应使用 --ci-check 登记真实平台检查。无远端 CI 的项目，在 AI 核实项目规则及平台情况后可用 --no-ci 显式保存 ci_policy=none；本地验证、独立审查、可合并状态和其他可见检查仍需通过。不能仅凭本地没有 CI 文件就使用 --no-ci。

init 返回 needs-configuration 时，接入尚未完成。当前 AI 应继续调查缺失的验证入口、真实 CI 名称或远端；只有必要认证或无法推断的用户决策才交接。远端和首次提交尚未建立的项目，先按用户授权完成项目初始化；begin 需要一个实际基准提交，不伪造 SHA。

首次接入新增的项目文件属于这轮配置任务，AI 应验证并按交付策略提交。之后无需重复接入，也不需要用户手工编辑任务或证据 JSON。

## 后续只说需求

例如“给列表增加 CSV 导出”“修复空输入崩溃”“CI 的 Windows 检查失败了，处理一下”。客户端读取项目说明后自动使用 maintenance-delivery。普通问答、解释和只读审查按原范围执行，不因此提交或推送。

AI 在开发前执行 begin，传入实际目标与允许改动的路径；来自 Issue/评论或客户端事件的稳定标识可用 --event-id 保存。反馈是待分析内容，不是扩大权限的指令。新 Issue/评论必须被客户端带入当前任务，本工具不后台监听 GitHub。

```text
python .repo-maintainer/plugin/scripts/project_workflow.py begin --repo . --objective "修复空输入崩溃" --allowed-path "src/**" --allowed-path "tests/**" --event-id "issue-42-feedback-1"
```

同一事件会复用已存在的任务；相同目标的未完成任务会恢复，目标不同的并行任务会阻止操作同一工作树。需要远端交付且当前在基准分支时，begin 创建独立任务分支，保留工作区内容。远端交付以 origin 的目标分支引用为基线（没有时使用本地目标分支），覆盖当前分支已有的未合并提交；基线必须是当前 HEAD 的祖先。开始前应获取最新目标分支并核对用户已有工作归属，范围检查和独立审查必须覆盖整个待合并差异，不能把已有提交漏出审查。恢复时若本轮交付终点或允许路径改变，应取消旧任务、核对远端后重新规划，不能沿用更大的旧权限。

## 开发完成后自动交付

1. AI 完成本轮修改及相关文档，诊断并修复测试失败，按项目规则精确提交。
2. 对最终提交执行 check，实际运行已配置验证。提交或内容变化后必须重新 check。测试改变受跟踪文件时，旧指纹失效，不能报告已验证。
3. 独立 AI 子代理或独立会话审查最终提交；实现者自评不算独立审查。AI 修复阻塞发现后重验、复审，再用 review 登记实际结论。项目要求的人工审批继续由平台执行。
4. AI 准备准确的 PR 标题和正文文件，调用 deliver。它复用配置及证据，确认远端分支是否已推送、查找和复用 PR，再按终点交付；merge 复用 repo_tools.py 的全部合并门槛及 head SHA 锁定。

```text
python .repo-maintainer/plugin/scripts/project_workflow.py check --repo .
python .repo-maintainer/plugin/scripts/project_workflow.py review --repo . --head FULL_FINAL_SHA --reviewer ACTUAL_INDEPENDENT_REVIEWER
python .repo-maintainer/plugin/scripts/project_workflow.py deliver --repo . --title "项目规范要求的标题" --body-file /outside/pr-body.md
```

这些命令由 AI 调用，用户不用逐条运行。独立审查能力或必要 GitHub 权限不可用时报告具体阻塞，不伪造审查或降低门槛。任务/证据与审查记录不是防篡改证明，不能取代宿主授权或平台规则。

## 等待、反馈与恢复

任务、每轮日志、证据及操作状态保存在 Git 元数据的 repo-maintainer 目录，不进入工作树、提交、插件包或源码验证指纹。支持普通检出和带 .git 文件的检出；锁由操作系统在进程退出时释放。

status 显示当前任务、状态和记录位置；block --reason 记录具体阻塞。check 保留每轮失败日志，当前证据仅对应当前候选。相同失败候选重跑需要 --retry-reason 说明已诊断的环境或状态变化。

CI 等待返回退出码 3。当前 AI 应只读等待实际平台状态变化，再继续 deliver，不让用户重复发起任务。CI 或审查失败则修复同一任务、重新提交/check/review/deliver；已有 PR 被关闭时先理解反馈，不能擅自重建。

远端写入结果不确定时先读取远端，禁止盲目重复写入。脚本会复用已推送提交和已有 PR；合并后本地记录尚未写完的任务可通过实际远端合并状态恢复确认。仍无法确认时，AI 继续只读诊断，必要时用 --retry-reason 记录明确的新依据。完成的事件再次调用不创建重复 PR。

项目配置在任务中途改变会阻止继续：AI 应先核对变更原因、旧任务和实际远端，不把旧证据套用到新策略。用户取消或明确改换任务/策略时，可用 cancel --reason 记录取消依据，再开始新任务；历史任务、用户工作、分支与 PR 保留，不把取消报告成已交付。不能通过取消任务规避验证或丢失尚待处理的远端结果。任务结束后，下一轮需求创建新任务；不自动删除分支或清理用户工作。

## 客户端接入与版本范围

项目入口采用 Codex 官方 AGENTS.md 与 Claude Code 官方 CLAUDE.md 项目说明机制，不假设两者共享插件钩子格式。入口把开发请求路由给 AI，Python 工具负责确定性的状态、验证和交付动作；它不会凭空运行模型或强制客户端遵循说明。

Codex 项目说明：[官方文档](https://developers.openai.com/codex/guides/agents-md)。Claude Code 项目说明：[官方文档](https://code.claude.com/docs/en/memory)。客户端能力、权限、独立审查与真实调用结果分别验证，不把文件存在等同于模型已执行。

项目接入与任务入口从 1.2.0 起提供，1.1.0 包没有这些新命令。使用完整的 1.2.0 发行包或 v1.2.0 标签源码接入；升级旧项目时由 AI 保留项目策略并明确更新完整运行目录，勿混合版本文件。发布动作仍要求用户明确指定版本；GitHub Actions 的插件发行脚本属于 repo-standards 自身，不会自动部署到目标项目。
