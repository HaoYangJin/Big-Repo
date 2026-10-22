# 安装与接入 Big-Repo

## 完整插件

从 [Releases](https://github.com/HaoYangJin/Big-Repo/releases) 获取正式发行。2.1.0 目标制品为 Big-Repo-2.1.0.zip、同名 .sha256 和 INSTALL-2.1.0.md；源码候选或本地构建不代表已正式发布。

Python 3.11+、Git 是运行前提；GitHub 操作需要已认证的 gh。用 sha256sum -c 校验，macOS 可用 shasum -a 256 -c，PowerShell 可用 Get-FileHash -Algorithm SHA256 比较摘要。完整解压到新目录，ZIP 顶层为 Big-Repo/。

将完整目录交给支持本地插件的客户端；也可让 AI 直接读取 skills/repo-intake/SKILL.md。Codex 的项目说明使用 AGENTS.md，Claude Code 使用 CLAUDE.md；客户端市场安装方式以实际版本支持为准。清单与相对路径约定参考 [OpenAI 官方插件文档](https://developers.openai.com/plugins/build/plugins)。

本仓库的 .agents/plugins/marketplace.json 与 .claude-plugin/marketplace.json 都指向根目录插件，内部 ID 为 big-repo，市场 ID 为 big-repo-local。只复制单个技能时，应复制完整技能目录；工作流脚本和探索台需要完整插件。

## 接入与使用

让 AI 阅读目标项目规则、验证命令、真实 CI、远端及分支，再执行 scripts/project_workflow.py init。新的安全接入接口默认仅本地提交，保存配置并复制 core 运行目录；不写 AGENTS.md / CLAUDE.md，不改已有 README 或添加体验页。本节面向 2.1.0，实际公开状态与制品以 Releases 为准。

```sh
python scripts/project_workflow.py init --repo /path/to/project --dry-run
python scripts/project_workflow.py init --repo /path/to/project
# 显式开启客户端入口与 PR 交付；自动合并需改为 --delivery merge
python scripts/project_workflow.py init --repo /path/to/project --update --client codex --delivery pr
# 展示需要 full 资源，local 不请求公开图表
python scripts/project_workflow.py upgrade --repo /path/to/project --delivery pr --client codex --profile full
python scripts/project_workflow.py init --repo /path/to/project --update --showcase local
```

公开展示显式选择 --showcase public（兼容 --public），工具核实仓库确实公开；远端的 --visibility public 不自动授权展示。未知或私有仓库使用本地内容。返回 needs-configuration 表示验证或 CI 信息待补齐，不能当作成功接入。重复 init 保留配置，配置更新需 --update；资源集合变更使用 upgrade。

显式启用客户端入口后，客户端根据需求执行已配置流程。普通问答、规划和只读审查不创建交付任务。工具仅核对通过自身执行的操作，不能拦截客户端直接运行 Git；配置、验证证据和审查登记均属于协作记录。详见 [工作流](../references/project-workflow.md)。

## 升级与回退

1.x 不直接混合覆盖。先保留旧版和项目配置，再按 [迁移说明](migration.md) 显式升级；迁移后重新验证和独立审查。回退需要完整旧运行目录及原配置，历史标签和附件不移动、不覆盖。

2.0 项目先用新版 status 查看历史策略，再显式运行 upgrade；不能把旧版默认 merge 当作已确认授权。升级或解除接入前先完成或显式取消活动任务。core 目录不包含完整资源，升到 full 时须从完整新版插件目录调用 upgrade；资源不足会在写入前拒绝。disconnect 移除有效客户端托管段并停用接入，保留 README、运行目录、日志及 PR。

社交图片位于源码 assets/social-preview.png，可用于 GitHub Settings → Social preview。生成图片或安装插件不自动修改全局客户端配置。
