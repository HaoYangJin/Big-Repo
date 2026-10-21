# 安装与接入 Big-Repo

## 完整插件

从 [Releases](https://github.com/HaoYangJin/Big-Repo/releases) 获取正式发行。2.0.0 制品为 Big-Repo-2.0.0.zip、同名 .sha256 和 INSTALL-2.0.0.md；源码候选或本地构建不代表已正式发布。

Python 3.11+、Git 是运行前提；GitHub 操作需要已认证的 gh。用 sha256sum -c 校验，macOS 可用 shasum -a 256 -c，PowerShell 可用 Get-FileHash -Algorithm SHA256 比较摘要。完整解压到新目录，ZIP 顶层为 Big-Repo/。

将完整目录交给支持本地插件的客户端；也可让 AI 直接读取 skills/repo-intake/SKILL.md。Codex 的项目说明使用 AGENTS.md，Claude Code 使用 CLAUDE.md；客户端市场安装方式以实际版本支持为准。清单与相对路径约定参考 [OpenAI 官方插件文档](https://developers.openai.com/plugins/build/plugins)。

本仓库的 .agents/plugins/marketplace.json 与 .claude-plugin/marketplace.json 都指向根目录插件，内部 ID 为 big-repo，市场 ID 为 big-repo-local。只复制单个技能时，应复制完整技能目录；工作流脚本和探索台需要完整插件。

## 接入与使用

让 AI 阅读目标项目规则、验证命令、真实 CI、远端及分支，再执行 scripts/project_workflow.py init。默认写入 .big-repo/config.json、.big-repo/plugin/、AGENTS.md / CLAUDE.md 托管段，以及 README 展示区和 docs/big-repo-explorer.html。

公开性核实后可加 --public；未核实时按私有处理。返回 needs-configuration 表示尚有验证或 CI 信息待补齐，AI 应继续调查，不能当作成功接入。

接入后正常提出开发需求或反馈即可。工具保存任务状态，客户端完成开发、展示同步、精确提交、验证、独立审查与交付。详见 [工作流](../references/project-workflow.md)。

## 升级与回退

1.x 不直接混合覆盖。先保留旧版和项目配置，再按 [迁移说明](migration.md) 显式升级；迁移后重新验证和独立审查。回退需要完整旧运行目录及原配置，历史标签和附件不移动、不覆盖。

社交图片位于源码 assets/social-preview.png，可用于 GitHub Settings → Social preview。生成图片或安装插件不自动修改全局客户端配置。
