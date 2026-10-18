# 双平台加载与发行包验收

1.1.0 将 Codex 与 Claude Code 作为两个独立验收目标；不要求调用模型、登录 Claude 或在用户电脑安装 Claude Code。离线脚本检查与真实宿主加载分别记账。

## 云端执行

Checks 工作流保留 Python 3.11 的 Windows、macOS、Ubuntu 测试，并增加两个 Ubuntu 作业：`plugin-load (codex)` 和 `plugin-load (claude-code)`。分别通过 npm 安装官方 Codex 0.163.0、Claude Code 2.1.302 到 runner 临时目录，不复用用户配置。

每个作业从当前提交构建实际 ZIP，校验资源和摘要后解压到带空格路径。Codex 登记隔离本地市场、安装启用，再由 app-server 返回六技能；Claude Code 使用 validate 和临时 `--plugin-dir` 加载后清点六技能。随后运行该安装目录中的工具，覆盖只读快照、私有媒体拦截、公开图表预览、代码示例、缺失链接、明暗素材和重复生成。

随包工具的测试目标是临时 Git 仓库，调用前后检查 README 和工作区状态；预览由测试夹具接收，不写入项目。CLI 命令不包含模型任务，移除常用 API 令牌环境变量并隔离 CODEX_HOME、CLAUDE_CONFIG_DIR。

## 查看证据

在最终 PR 的 Checks 中核对五项检查均成功，下载两个 `host-verification-*` 工件。其中 `host-verification.json` 必须为 `verified-host`，技能数为六、`model_calls` 为 false；`source_sha` 必须等于待合并 head，`archive_sha256` 必须与实际发行 ZIP 相同。

`distribution.json` 还记录工作区是否脏、资源数和可复现结果。工件保存七天；正式发行另附不含凭据的验收 JSON，长期保留。文档中的命令和历史成功记录不能代替当前提交的运行结果。

## 本地复现

在源仓库根目录执行，输出目录放在仓库之外：

```text
python scripts/verify_plugin.py --output /outside/distribution
python scripts/check_host.py --host codex --cli /absolute/path/to/codex --output /outside/codex-check
python scripts/check_host.py --host claude-code --cli /absolute/path/to/claude --output /outside/claude-check
```

脚本不会下载 CLI；需提供上述固定版本的可执行文件。仅当用户主动选择本地验证时执行宿主命令。JSON 的 `handoff` 表示未通过，不自动改称跳过。模型语义执行、桌面交互和全部六技能端到端任务不在本次验收范围内。
