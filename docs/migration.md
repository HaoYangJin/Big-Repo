# 1.x → Big-Repo 2.0.0

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

先备份并检查工作区与任务，使用完整 2.0.0 源码或解压包执行：

```sh
python /path/to/Big-Repo/scripts/project_workflow.py init --repo /path/to/project --migrate
```

只有确实同时更名了目标项目的 GitHub 仓库，才使用 --repository owner/new-name 明确新的身份；普通项目沿用原有 repository 字段。

迁移保留交付终点、验证命令、CI、分支、用户说明、任务身份、日志及 PR 关联。仅替换托管说明段；旧项目目录备份到 Git 元数据的 big-repo/legacy-project-backup，旧任务目录也保留供恢复。

活动任务的旧验证证据归档，新状态恢复为 working，随后必须精确提交、check、独立审查及 review，不能把旧证据套到新候选。闭合任务保持闭合。

新旧配置、运行目录或状态发生冲突时拒绝覆盖；策略与旧任务摘要不一致时先核对原因。迁移中断后检查 migration.json、两侧目录和配置，不删除任一侧来规避门槛。

## 回退

先确认远端写入结果和任务状态。在独立目录使用原版完整插件与备份配置恢复；保留新旧日志，不让同一工作树同时运行两套交付器。必要时将备份项目文件恢复到原相对位置，再由旧版 status 检查。不要移动既有标签或覆盖发行附件。
