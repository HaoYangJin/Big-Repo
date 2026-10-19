# 仓库展示与离线玩法

1.3.0 把可视化和体验放回本仓库首页：Mermaid 交付流程、真实浏览器截图、可运行的离线探索台与贡献入口。主入口仍是接入和交付；展示不作为每次开发的强制治理步骤。

## 两分钟体验

在源码根目录运行：

```sh
python plugins/repo-maintainer/scripts/explore.py --demo --output ../Repo-Standards-demo.html
python plugins/repo-maintainer/scripts/explore.py --repo . --output ../Repo-Standards-report.html
```

用浏览器打开 HTML，无需服务器、账号、前端依赖或网络。每次使用新输出路径；工具不覆盖已有文件。完整发行包在解压后的 Repo-Standards 目录运行 `python scripts/explore.py`，参数相同。

- **看结构**：显示采集时间、HEAD、分支、工作区是否干净、Git 跟踪路径数，以及 README、根目录协作规则、tests/test 目录和 GitHub 工作流的存在性。
- **试交付**：顺利交付、测试失败、独立审查阻塞、CI 等待四种场景；阻塞时“下一步”不可用，显式模拟解决后才能继续。切换场景或重新开始会清空演练进度。
- **选玩法**：筛选本地可用或公开仓库适用的六类展示方式。
- **带走快照**：导出 Markdown，保留数据类型、时间与提交身份，不导出演练作为真实验证证据。

结构信号只是启发式检查，不计算质量分或可合并分。只查 Git 跟踪路径，不读取文件内容；被跟踪但已删除的文件仍属于索引信号，工作区会标记为有改动。其他测试目录和非 GitHub CI 可能未被识别，未发现不等于项目没有相应能力。真实 CI、验证与审查继续由 project_workflow / repo_tools 执行。

## 本仓库采用与维护约定

| 展示 | 来源与维护 | 移除方式 |
| --- | --- | --- |
| 首页 Mermaid 流程 | 与实际交付门槛同步，不冒充运行状态 | 删除流程代码块 |
| 探索台截图 | 用 `--demo` 固定数据生成，浏览器实际截图，不含项目私有内容；界面变化后重拍 | 删除 README 图片与 docs/assets/explorer-demo.png |
| 离线探索台 | Python 标准库 + 内嵌 HTML/CSS/JS，零外部请求；打包必须包含 assets/explorer.html | 删除生成的 HTML；移除功能时同时更新脚本、资源、测试和入口 |
| 参与与版本入口 | 真实 CONTRIBUTING、Issues、贡献记录、Actions、Releases、CHANGELOG | 修改对应链接 |

生成 HTML 不会修改被检查仓库；但用户主动把输出路径放进仓库时会产生一个文件，建议放在仓库外。快照包含仓库名、分支名和提交标识，分享前应检查。页面不存储浏览器持久数据、不向第三方发送标识。

## 历史与可选扩展

1.1.0 及此前曾采用 Star History、Shields 和 Checks 徽章，1.2.0 将它们移到历史资料且没有提供交互替代。1.3.0 使用本地可视化和演练作为稳定入口。外部图表不随页面自动加载；公开仓库仍可按需加入真实图表并保留文字回退，私有或公开性未知仓库不发送标识到公开服务。

参考：[六类玩法目录](../plugins/repo-maintainer/skills/repo-showcase/references/showcase-catalog.md)、[Star History](https://github.com/star-history/star-history)、[GitHub 工作流徽章](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge)、[Shields](https://github.com/badges/shields)。历史可用性检查只代表当时状态，不作为本版本远程服务验收证据。
