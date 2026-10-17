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

### Codex

使用支持本地插件市场的客户端，在克隆的仓库中选择 `repo-standards-local` 本地市场并安装 `repo-maintainer`。仓库 `.agents/plugins/marketplace.json` 只声明可发现项，不启用插件。不同客户端的发现和重启要求请按 [官方安装说明](https://developers.openai.com/plugins/build/plugins) 操作。

从 ZIP 取得插件时，先完整解压到所需项目的 `plugins/repo-maintainer/`，再按官方说明主动添加本地市场项，将 source.path 指向该目录。不要只复制清单或单个 SKILL.md；本交付不会替用户安装或启用。

### Claude Code

使用本地目录做临时加载，不写入用户配置：

```text
claude --plugin-dir /absolute/path/to/plugins/repo-maintainer
```

或主动添加本仓库的市场再安装。私有来源仍需要读取权限；安装不会授予其他项目的修改权限。参考 [官方插件文档](https://code.claude.com/docs/en/plugins)。

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
