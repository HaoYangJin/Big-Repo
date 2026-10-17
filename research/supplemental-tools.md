# 补充案例：仓库展示工具

核验日期：2026-10-18。以下不占核心 60 个样本名额，不参与六类分母统计。功能来自各项目官方仓库说明；可用性、账户条件、费用和配额以实际接入时为准。

| 工具 | 已核实的用途 | 本插件采用方式与边界 |
| --- | --- | --- |
| [Star History](https://github.com/star-history/star-history) | 星标历史图、日期或时间线视图，以及 README 嵌入入口 | 为确认公开且明确选择的仓库提供图表模板与文字回退；不把 Star 当使用人数，不请求当前私有仓库的统计 |
| [Shields](https://github.com/badges/shields) | 可嵌入的状态徽章 | 仅展示真实包、版本、CI 或许可证；未知指标不填充虚假值。私有仓库默认本地静态素材 |
| [All Contributors](https://github.com/all-contributors/allcontributors.org) | 贡献者致谢规范、网站与机器人文档 | 可以生成来自真实记录的静态致谢；不会因为修改 README 就安装机器人或授予写权限 |
| [StackBlitz WebContainers](https://github.com/stackblitz/webcontainer-core) | 浏览器中的开发环境能力 | 技能按技术栈推荐已验证体验入口，库的存在不代表任意仓库都能一键运行；创建在线环境或部署属于单独授权 |

## 固定验收

选择功能后检查其真实来源、数据覆盖、权限、服务依赖、成本、失效回退与移除方式。
保存截图和录屏前检查敏感内容与素材许可；第三方统计不可用时不影响核心安装、贡献或版本说明。
这些工具不是 OpenAI 或 Anthropic 为本插件背书的依赖，也不由插件默认启动。
