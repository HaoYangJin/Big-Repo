# Big-Repo 版本迁移

## 2.0 → 2.1 安全策略升级

2.1 新接入默认 commit、无客户端常驻入口、core 资源且不生成展示。旧配置仍可查询，但必须显式选择策略后才能用新版开始任务或远端交付；不要覆盖旧版配置来跳过确认。

```sh
python scripts/project_workflow.py status --repo /path/to/project
python scripts/project_workflow.py upgrade --repo /path/to/project --delivery commit --client none --profile core --dry-run
python scripts/project_workflow.py upgrade --repo /path/to/project --delivery commit --client none --profile core
# 已明确授权自动合并的项目，可自行选择 --delivery merge --client both
python scripts/project_workflow.py disconnect --repo /path/to/project --dry-run
```

活动任务必须先用原运行目录完成，或经用户明确取消后再升级；取消保留用户工作、分支、日志和 PR。升级保留历史记录，旧证据不能用于新提交。schema v2 记录实际选择和运行版本，记录不构成防篡改的人类授权证明。

升级在 Git 元数据内保存项目文件与旧运行目录备份，采用暂存校验及替换；非托管运行文件或异常说明标记拒绝覆盖。写入失败会回滚，再次执行会尝试恢复已登记的中断；恢复发现外部修改时停止，保留现场。回退时先确认远端结果，在独立目录使用备份配置和完整旧运行目录，不改写已有标签或附件。

解除接入只移除客户端有效托管段并停用配置，不删除用户说明、README、运行目录或任务记录。重新启用需显式 init --update；客户端策略和资源集合仍须核对。

## 更名对照

| 1.x | 2.0.0 |
| --- | --- |
| Repo-Standards / repo-maintainer | Big-Repo / big-repo |
| repo-standards-local | big-repo-local |
| plugins/repo-maintainer/ | 源码根目录 |
| .repo-maintainer/config.json | .big-repo/config.json |
| .repo-maintainer/plugin/ | .big-repo/plugin/ |
| Git 元数据内 repo-maintainer/ | Git 元数据内 big-repo/ |

GitHub 仓库现在为 HaoYangJin/Big-Repo。更新克隆的 origin；旧仓库链接的重定向以 GitHub 实际状态为准。旧 Release、附件和标签保留原貌。已安装的全局旧插件需由用户主动切换，不静默替换。

## 显式迁移

先备份并检查工作区与任务，用原版运行目录完成活动任务，或按用户指令用原版 cancel --reason 显式取消，再从完整新版源码或解压包执行命名空间迁移：

```sh
python /path/to/Big-Repo/scripts/project_workflow.py init --repo /path/to/project --migrate
```

只有确实同时更名了目标项目的 GitHub 仓库，才使用 --repository owner/new-name 明确新的身份；普通项目沿用原有 repository 字段。

迁移保留交付终点、验证命令、CI、分支、用户说明、任务身份、日志及 PR 关联。仅替换托管说明段；旧项目目录备份到 Git 元数据的 big-repo/legacy-project-backup，旧任务目录也保留供恢复。

2.1 拒绝迁移未闭合的旧任务，避免旧策略确认与活动任务互相阻塞。闭合任务保留身份、PR 关联、历史证据与状态；这些历史证据不能用于新候选。命名空间迁移后仍须用 upgrade 显式选择交付、客户端和资源策略。

新旧配置、运行目录或状态发生冲突时拒绝覆盖；策略与旧任务摘要不一致时先核对原因。迁移中断后检查 migration.json、两侧目录和配置，不删除任一侧来规避门槛。

## 回退

先确认远端写入结果和任务状态。在独立目录使用原版完整插件与备份配置恢复；保留新旧日志，不让同一工作树同时运行两套交付器。必要时将备份项目文件恢复到原相对位置，再由旧版 status 检查。不要移动既有标签或覆盖发行附件。

core 运行目录升级到 full 时，请从完整新版插件调用 upgrade。若 status 返回 recovery-required，先在无活动任务时重试原 upgrade 或 disconnect；init、begin 和 deliver 在恢复前拒绝继续，status 不自动写入恢复结果。
