# 首页展示维护说明

本仓库已公开；首页实际接入 Star History、GitHub 工作流徽章、Shields 版本/星标徽章，并提供下载卡片、可运行的本地体验、贡献入口和有来源的项目足迹。它们是本仓库对 repo-showcase 的一次应用，不要求其他项目照搬。

## 已采用的功能

| 功能与用途 | 数据来源、权限和成本 | 更新与失效处理 | 移除方式 |
| --- | --- | --- | --- |
| Star History 明暗主题图，观察公开星标记录 | api.star-history.com 读取公开仓库标识，无令牌、无需仓库写入权限；读者浏览时会访问外部图片，受服务缓存、限流与可用性影响 | 第三方动态更新，具体更新时间未知；零 Star 不推断增长，失效后用文字入口和 GitHub 星标记录 | 删除 activity 区的 picture/a 图表与对应引用，不影响文字导航 |
| GitHub 原生 Checks 徽章，进入真实检查结果 | GitHub 公开 check.yml 的最近 pull_request 事件；无需新工作流或权限，徽章不是指定提交验收证据 | 工作流改名或事件调整时更新 URL；失败/等待按实际显示，异常时查看 Actions 文字入口 | 删除 frontpage 区 Checks 图片及链接 |
| Shields Release/Stars 徽章，快速进入版本与星标页面 | img.shields.io 读取公开 GitHub 数据，无账号或写入权限；受上游缓存影响 | 发行前版本可能未知；不硬编码成功或数字，查看 GitHub 原始页面核对；迁移仓库时更新标识 | 删除对应徽章，保留发行与星标文字链接 |
| 下载卡片与两分钟体验，缩短初次使用路径 | 仓库内资料、Python 标准库和已存在脚本；运行用户本地只读检查，不创建在线环境 | 发布时更新版本与附件名，命令变化时同步；无 Python 时仍可阅读技能和文档 | 删除卡片或示例，不卸载任何环境 |
| 贡献导航，帮助读者找到参与入口 | 已存在 CONTRIBUTING、公开 Issues 与 GitHub 真实贡献者页面；未启用 Discussions、贡献机器人或写权限 | 仓库功能或页面迁移时更新；没有记录不虚构贡献者墙或入门任务 | 删除链接，不涉及撤销机器人权限 |
| 项目足迹与可展开的维护故事，展示真实演进 | 仓库规范、研究索引、PR #1、PR #2 和每轮自审记录；无统计服务 | 有实际新里程碑时人工更新，未发布不写已发布；来源失效时改为固定提交或移除该行 | 删除对应表格行或 details 区块 |

本轮检查公开 API 图表、CI 与星标徽章均返回 SVG；发行前版本徽章返回无可用版本是预期状态，正式发布后另行核对。可用性只代表检查时刻，不能保证未来或每个读者网络可访问。来源采集：2026-10-18。

## 更新约定

首页用 `repo-maintainer:frontpage` 与 `repo-maintainer:activity` 两组 start/end 注释标识展示区；修改时更新已有区，不再次追加。它们是人工维护区，不是脚本 preview 的 `repo-maintainer:showcase` 自动生成区；不要把完整 preview 输出直接覆盖首页。

日常变更只核对是否影响版本、命令、链接、图表标识或故事来源；无关修改不追加装饰。外部服务不支持当前网络时保留文字入口，不自动创建定时 Actions、代理服务、部署或令牌配置。要关闭全部外部图片，删除三枚徽章与 Star History picture 即可，正文与插件仍可正常使用。

## 参考

- [Star History 项目](https://github.com/star-history/star-history)
- [GitHub 工作流徽章说明](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge)
- [Shields 项目](https://github.com/badges/shields)
- [插件六类玩法目录](../plugins/repo-maintainer/skills/repo-showcase/references/showcase-catalog.md)
## 1.1.0 检查器补充

可点击徽章的图片和点击目标分别检查，HTML 锚点也检查相对链接；引用标签连续空白统一归一。围栏代码、行内代码及注释中的示例不当作实际展示。HTML 属性内的反引号和注释字样保留为属性文字，避免隐藏真实媒体。此实现为有界扫描，不能代替完整渲染与远程可用性验证。
