# repo-maintainer

帮助开发者把明确的仓库维护任务交给 AI，验证与审查通过后自动合并 PR；同时提供版本发布准备和仓库展示能力。

## 能力与边界

| 技能 | 使用场景 |
| --- | --- |
| repo-intake | 接管仓库，确认规则、范围、验证入口和展示现状 |
| maintenance-delivery | 缺陷修复、依赖更新、文档同步，验证与审查通过后自动合并 PR |
| repo-audit | 按仓库类型检查维护、发布与展示流程 |
| release-preparation | 准备版本说明、兼容性和发布清单，不执行发布 |
| skill-maintenance | 编写、修改或审查 SKILL.md 与配套资源 |
| repo-showcase | 推荐、生成、审查及修复仓库展示内容 |

默认在首次非预期验证失败或必要权限缺失时交接，不自动修复重试。默认经验证和独立审查后自动合并；不正式发布、不部署，不在后台持续运行。预先声明的测试开发红灯与故障注入不是交付验证失败；必须在执行前标明其预期失败条件，不得事后改称预期失败。

## 安装与平台状态

整个插件目录包含共享工具，发布包应整体复制。现有项目的规则优先；本插件不修改全局配置。

1.0.0 已在隔离目录完成 Codex 插件安装、启用和六技能发现，以及 Claude Code 的清单校验、加载和六技能清点。隔离环境未登录模型账号，模型驱动典型任务尚未验证；此结果不等于桌面界面测试或完整端到端验收。

### 获取与校验 1.0.0

从 [GitHub Releases](https://github.com/HaoYangJin/repo-standards/releases/tag/v1.0.0)下载 `repo-maintainer-1.0.0.zip` 和同名 `.sha256` 文件。此处为该版本的发行入口，发布前链接尚不可用。ZIP 仅包含插件目录；完整研究档案请读取源仓库。

Windows PowerShell 可计算校验值，与 `.sha256` 第一列比较：

```powershell
Get-FileHash ./repo-maintainer-1.0.0.zip -Algorithm SHA256
Get-Content ./repo-maintainer-1.0.0.zip.sha256
Expand-Archive ./repo-maintainer-1.0.0.zip -DestinationPath ./repo-maintainer-1.0.0
```

macOS/Linux 可使用自带 Python：

```text
python3 -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('repo-maintainer-1.0.0.zip').read_bytes()).hexdigest())"
python3 -m zipfile -e repo-maintainer-1.0.0.zip repo-maintainer-1.0.0
```

解压后插件根目录为 `repo-maintainer-1.0.0/repo-maintainer/`。升级时先停用旧版本，保留项目规则与本地改动，在新目录解压并重新指向它；回退时重新选择原插件目录或固定的旧提交。勿混合覆盖不同版本的单个文件。

### Codex

使用支持本地插件市场的客户端，在克隆的仓库中选择 `repo-standards-local` 本地市场并安装 `repo-maintainer`。仓库 `.agents/plugins/marketplace.json` 只声明可发现项，不启用插件。不同客户端的发现和重启要求请按 [官方安装说明](https://developers.openai.com/plugins/build/plugins) 操作。

支持该命令的 Codex CLI 可登记固定版本的源码市场，再在桌面客户端插件目录中选择 `repo-standards-local` 安装并开启新会话：

```text
codex plugin marketplace add HaoYangJin/repo-standards --ref v1.0.0
```

以上是用户主动安装时执行的命令，本发行过程不执行它，也不修改用户级设置。旧客户端缺少该命令时采用前述克隆仓库的本地市场方式。

从 ZIP 取得插件时，先完整解压到所需项目的 `plugins/repo-maintainer/`，再按官方说明主动添加本地市场项，将 source.path 指向该目录。不要只复制清单或单个 SKILL.md；本交付不会替用户安装或启用。

### Claude Code

使用本地目录做临时加载，不写入用户配置：

```text
claude --plugin-dir /absolute/path/to/plugins/repo-maintainer
```

如果使用上述 ZIP 解压目录，在同一工作目录执行 `claude --plugin-dir ./repo-maintainer-1.0.0/repo-maintainer`。

或主动添加本仓库的市场再安装。私有来源仍需要读取权限；安装不会授予其他项目的修改权限。参考 [官方插件文档](https://code.claude.com/docs/en/plugins)。

支持一条命令安装市场插件的 Claude Code 2.1.275+ 可在会话中主动执行：

```text
/plugin install repo-maintainer --marketplace HaoYangJin/repo-standards
```

这条命令从仓库默认分支取得插件；需要固定 1.0.0 时使用发行 ZIP 与 `--plugin-dir`。

客户端实际加载测试结果见仓库的验收报告；JSON 和目录校验通过不能替代真实平台加载验证。

## 工具用法

要求 Python 3.11+、Git；研究采集和 PR 查询还需要已登录的 GitHub CLI。均不需要额外 Python 包。在插件根目录执行：

```text
python scripts/repo_tools.py snapshot --repo /path/to/repository
python scripts/repo_tools.py preflight --repo /path/to/repository --task /outside/task.json
python scripts/repo_tools.py accept --repo /path/to/repository --task /outside/task.json --evidence /outside/evidence.json
python scripts/repo_tools.py merge-readiness --repo /path/to/repository --task /outside/task.json --evidence /outside/evidence.json --pr owner/name#123
python scripts/repo_tools.py showcase --repo /path/to/repository
python scripts/repo_tools.py preview --repo /path/to/repository --repository owner/name
python scripts/repo_tools.py pr --pr owner/name#123
```

`preview` 仅向 stdout 输出候选 README；不会改文件或请求网络。默认按私有仓库处理，公开仓库须显式加 `--public`。加入 Star History 还需显式加 `--star-history`，且必须已确认公开性。生成后查看差异并检查链接，再按授权应用。

检查输出默认 JSON，可加 `--format markdown`。退出码 0 表示对应检查完成，2 表示需要交接，3 表示 CI 或合并状态尚待 GitHub 完成计算，可只读等待。`verified-local` 不表示远端验证、推送或 PR 已完成；必须另行查询 PR，并核对 head SHA、目标分支、状态与检查结果。

### 验证证据

从任务模板填写实际目标与命令，将任务和证据保存在仓库之外，避免改变待验代码的指纹。先在该版本运行约定验证，再执行 snapshot，把指纹与真实结果填入证据模板。提交会改变指纹；提交后应对最终版本重新验证、重新生成证据，再推送。

指纹覆盖跟踪文件和非忽略未跟踪文件；不覆盖忽略文件、子模块内部、运行环境或外部服务。依赖这些内容的验证必须另附版本与人工审查证据。证据由调用方声明，非防篡改签名，工具不证明用户授权真实性或测试充分性。

PR 查询只读且不自动重试；权限不足时交接。展示审查默认离线，不验证远程可用性或页内锚点，报告中明确标为未验证。外部媒体检查保守拦截私有仓库的所有外部图片，以便开发者逐项审查。

## 研究与模板

[研究实践矩阵](references/practice-matrix.md)与[来源索引](references/sources.md)提供共性、差异和固定来源；`templates/` 提供任务、证据、交接和展示草稿。模板中的示例值必须替换，模板本身不产生执行授权。

研究采集器使用公开 GitHub 读取接口，完整档案保留在源仓库，插件仅携带精简索引。网络采集可对临时传输故障有限重试；维护任务的“首次失败交接”不因此改变。

## 自动合并与可复现打包

任务允许 merge 时，merge 配置必须声明 repository、base_branch 和非空 required_checks；验证证据还必须包含绑定最终 head_sha 的独立审查记录 review（status 为 approved、真实 reviewers 非空、blocking_findings 为 0）。这些记录是调用方声明，不是防篡改的授权或审查证明。

merge-readiness 只读检查本地证据、清洁工作区、PR 身份和分支、最终提交、非草稿、无阻塞审查、登记的 CI 和其他可见检查全部成功、GitHub 可合并且状态 CLEAN。缺失、跳过、取消、失败均不通过；等待不触发修复。合并仍由代理按宿主权限执行：

```text
gh pr merge NUMBER --repo OWNER/REPO --squash --match-head-commit VERIFIED_SHA
```

不使用 --admin，不删分支；项目不支持 squash 时交接。用户明确限制为只审查、只本地或只 PR 的任务优先，不因默认自动合并扩大范围。正式发布、标签、制品上传和部署继续独立授权。

从源仓库根目录构建，不安装或发布任何内容：

```text
python scripts/build_plugin.py --output dist
```

输出版本化 ZIP 和对应 .sha256 文件。固定条目时间、排序和权限，UTF-8 文本统一 LF，使用无压缩条目避免压缩库差异；相同文件内容得到相同字节。缓存、临时目录、凭据文件和符号链接不进入包。输出必须在插件目录之外。

1.0.0 使用目标目录中的独立随机临时文件，全部准备完成后逐个原子替换 ZIP 与校验和，异常退出时清理本次临时文件；不覆盖固定名称的其他临时文件，也不打开已有输出符号链接的目标。两次替换不构成跨文件事务：后一步失败可能留下新 ZIP 与旧校验和，工具会报错交接，不能分发；分发前必须重新核对摘要。输出目录应由调用方控制，同一版本不要并发发布。
