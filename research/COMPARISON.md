# 官方仓库的共性、差异与 AI 维护建议

## 结论与证据级别

可复用的不是某一家公司统一的文件清单，而是：先找到项目真实规则与生成源，明确责任和验证证据，再按项目发布渠道交付。展示功能应帮助理解项目，并承担与其价值相称的维护成本。
这是一项有边界的案例研究。档案深入到配置、真实变更与发布关联，但未穷尽源码、平台权限、外部 CI 或全部历史；候选信号统计与下文人工核对的案例分开解释。

## 采集覆盖

固定样本 60 个，读取文档/配置/代表入口 1333 个，默认分支提交 1200 条，已合并 PR 172 个，正式 GitHub Release 160 个。
关联 Actions 运行记录 3033 条（未按 run ID 全局去重），接口错误 0 条。实际状态、时间和限制以各档案为准。

[全部分类档案](README.md) · [方法与限制](METHODOLOGY.md) · [机器可读统计](summary.json) · [来源索引](source-index.json)

## 按内容类型比较

| 类型 | 主要维护对象与差异 | AI 托管的关键适配 |
| --- | --- | --- |
| SDK | 生成源、手写扩展、语言运行时及包注册表；同一组织的不同语言 SDK 也可能采用不同生成器 | 先核对可编辑边界与生成流程，再选择兼容性测试和版本更新 |
| 代理、技能与协议 | 技能内容库、产品反馈仓库、协议实现与多包 SDK 交付物不同 | 先确认真正可修改的源码或内容，以及安装与平台行为的验证方式 |
| 模型与机器学习 | 构建、硬件、权重、可选依赖和测试矩阵带来环境差异 | 明确硬件与网络依赖，未运行的设备测试单列，不能以本地通过替代 |
| 应用与框架 | 多包、运行时、预发布与多条稳定维护线并存 | 固定受影响包、分支和通道，不只找一个“最新版本” |
| 基础设施 | 组件责任、兼容性、集群集成和多版本维护较重要 | 识别责任人和环境，变更验证与生产部署严格分开 |
| 语言与开发工具 | 自举、平台矩阵、镜像及非 GitHub 贡献渠道 | 先检查贡献入口和 AI 使用政策，不能默认所有项目都接受 AI 创建的 PR |

上表是跨案例解释和插件建议；不声称每个类别的所有仓库都采用同一种实现。

## 已核对案例：共性与不能统一的地方

### 生成代码要找源头，但“生成文件一律不能改”过于粗糙

OpenAI Python 的代理说明明确区分生成 SDK 与手写政策、测试和示例。Anthropic Python 进一步说明某些文件混合生成内容与手写内容，需要定位具体行的来源。OpenAI .NET 的贡献指南则描述 TypeSpec、Generated 与 Custom 目录。共性是定位来源，区别是定位和再生成机制。
[openai/openai-python/AGENTS.md:3](https://github.com/openai/openai-python/blob/bfada5040b0171cd0ae61aefae8c78fcf83c804a/AGENTS.md#L3)；[anthropics/anthropic-sdk-python/CLAUDE.md:9](https://github.com/anthropics/anthropic-sdk-python/blob/bcd55fe1d3f0f1240765f8cef04295b67337f55a/CLAUDE.md#L9)；[openai/openai-dotnet/CONTRIBUTING.md:9](https://github.com/openai/openai-dotnet/blob/25f107e53ad5f2500d6b33088056fca2404db305/CONTRIBUTING.md#L9)。

### 提交、版本与发布是关联流程，不是一套通用命令

Anthropic Python 的说明将结构化提交与 release-please 联系起来；MCP Python 的发布文档说明版本来自标签、发布工作流取自被标记提交，且存在不同发布线。Svelte 的贡献说明强调真实测试命令和 UI 改动的截图或视频。
[anthropics/anthropic-sdk-python/CLAUDE.md:354](https://github.com/anthropics/anthropic-sdk-python/blob/bcd55fe1d3f0f1240765f8cef04295b67337f55a/CLAUDE.md#L354)；[modelcontextprotocol/python-sdk/RELEASE.md:17](https://github.com/modelcontextprotocol/python-sdk/blob/2af9e3089ac66b35c1550c500aae86a82efb1e17/RELEASE.md#L17)；[sveltejs/svelte/CONTRIBUTING.md:85](https://github.com/sveltejs/svelte/blob/40bb08482f4857d91221638dec544a532bc35389/CONTRIBUTING.md#L85)。
插件因此记录验证命令、目标提交、受影响组件和发布通道，不把 Conventional Commits、某个发布工具或某个测试命令当成所有项目的强制规则。

### 责任和权限要有实际边界

Kubernetes 的 OWNERS 列出不同文件的 reviewers 与 approvers。OpenAI Python 的说明限制发布凭据与 OIDC 权限的使用范围。文件内容能证明项目声明了规则，不能单独证明平台设置已生效。
[kubernetes/kubernetes/OWNERS:5](https://github.com/kubernetes/kubernetes/blob/9b3380ed0f0882068abd7fb9bfbc816c595ae79e/OWNERS#L5)；[openai/openai-python/AGENTS.md:39](https://github.com/openai/openai-python/blob/bfada5040b0171cd0ae61aefae8c78fcf83c804a/AGENTS.md#L39)。

### 仓库身份和贡献渠道不能省略

Go README 明确说明 GitHub 镜像身份，贡献指南转向项目贡献文档。VS Code README 区分 Code - OSS 仓库和产品发行版。Rust 的代理说明要求遵守项目 LLM 使用政策。它们说明：维护对象、产品名称和可接受贡献方式都需要单独核对。
[golang/go/README.md:10](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/README.md#L10)；[golang/go/CONTRIBUTING.md:29](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/CONTRIBUTING.md#L29)；[microsoft/vscode/README.md:5](https://github.com/microsoft/vscode/blob/bc981cb296f12a2919e43b33a3a0444878a600cd/README.md#L5)；[rust-lang/rust/AGENTS.md:3](https://github.com/rust-lang/rust/blob/158f79d5c24d262f820fa45da96e7b77bc29a338/AGENTS.md#L3)。

AI 使用规则本身也存在差异：Neovim 的代理说明要求 AI-assisted 提交尾注，而 Rust 的说明包含更细的允许与禁止范围。插件必须读取目标项目的实际政策，不能把一种披露方式或限制推广到全部项目。
[neovim/neovim/AGENTS.md:3](https://github.com/neovim/neovim/blob/0851e7dabed9fc9c019e22088029f36e9f3ec3e3/AGENTS.md#L3)；[rust-lang/rust/AGENTS.md:10](https://github.com/rust-lang/rust/blob/158f79d5c24d262f820fa45da96e7b77bc29a338/AGENTS.md#L10)。

Helm 的代理说明明确区分 v3/dev-v3 与 v4/main；这与档案中同时出现多条稳定发布线一致。发布准备必须绑定组件和维护分支，而不是只修改一个最大版本号。
[helm/helm/AGENTS.md:10](https://github.com/helm/helm/blob/9b88efd62a6908fb11215f8e8b50c3c62a246df0/AGENTS.md#L10)。

### 技能仓库也有独立的打包与授权边界

Anthropic Skills 说明每个技能的独立目录、示例用途以及不同资源的许可证范围，不能把“公开可读”当作全部资源采用相同许可。插件据此保留资源归属、相对引用和运行环境，格式通过后仍单列平台加载验证。
[anthropics/skills/README.md:14](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/README.md#L14)。

## 固定维度：仓库展示与玩法

固定检查增长活动、状态徽章、项目门面、快速体验、社区参与和项目故事。采用情况与推荐价值分别记录；某个大型项目没有某项内容，不构成应当补齐的缺陷。
本次所查文件中 Star History 候选信号命中 0/60 个仓库；这不代表未查目录或历史版本也未使用。Star History 作为补充工具案例提供，不写成官方仓库的共同要求。
图片统计包含徽章，主题图片信号可能来自更新记录中的 HTML 说明，在线体验信号可能来自 bug 模板；不能把这些数字解释为完整功能采用率。
[六类玩法、依赖与移除方式](../plugins/repo-maintainer/skills/repo-showcase/references/showcase-catalog.md) · [可复用草稿](../plugins/repo-maintainer/templates/showcase.md)

## 候选信号分布

分子为至少一个已读文件命中关键词的仓库数，分母为该类档案数；这是发现线索，不是质量分数或规范遵循率。

| 类别 | 测试候选 | 生成代码提示 | 自动发布候选 | 徽章 | 主题图片候选 | 在线体验提及 |
| --- | --- | --- | --- | --- | --- | --- |
| API SDK | 6/10 | 10/10 | 9/10 | 8/10 | 0/10 | 1/10 |
| 代理、技能与协议 | 7/10 | 3/10 | 6/10 | 5/10 | 0/10 | 1/10 |
| 模型与机器学习 | 9/10 | 7/10 | 3/10 | 7/10 | 4/10 | 4/10 |
| 应用与框架 | 10/10 | 7/10 | 6/10 | 7/10 | 3/10 | 3/10 |
| 基础设施 | 7/10 | 7/10 | 2/10 | 9/10 | 3/10 | 3/10 |
| 语言与开发工具 | 8/10 | 8/10 | 5/10 | 8/10 | 5/10 | 5/10 |

## 转化为插件的决策

- 用任务记录绑定目标、范围、基准、操作和验证；项目现有规则优先。
- 将首次非预期失败交接设为本插件默认，不宣称它是 60 个仓库共同采用的策略。
- 本地验证、独立审查、远端 CI 和自动合并分别报告；自动合并锁定最终 head SHA，生成发布草稿仍不执行发布。
- 展示内容先预览，再在授权范围内应用；私有仓库不接入公开统计服务。
- 小型仓库保留最小有效流程，不强制复制大型组织的全部门禁。

## 身份迁移与缺口

- anthropics/anthropic-cookbook → anthropics/claude-cookbooks，保留原样本标识与解析后的来源。
- [anthropics/anthropic-cookbook](profiles/anthropics__anthropic-cookbook.md)：PR 3/3，正式 GitHub Release 0/3，接口错误 0。不足仅表示本方法取得的实际样本。
- [anthropics/claude-plugins-official](profiles/anthropics__claude-plugins-official.md)：PR 3/3，正式 GitHub Release 0/3，接口错误 0。不足仅表示本方法取得的实际样本。
- [anthropics/skills](profiles/anthropics__skills.md)：PR 3/3，正式 GitHub Release 0/3，接口错误 0。不足仅表示本方法取得的实际样本。
- [django/django](profiles/django__django.md)：PR 3/3，正式 GitHub Release 0/3，接口错误 0。不足仅表示本方法取得的实际样本。
- facebook/react → react/react，保留原样本标识与解析后的来源。
- [ggml-org/llama.cpp](profiles/ggml-org__llama.cpp.md)：PR 3/3，正式 GitHub Release 1/3，接口错误 0。不足仅表示本方法取得的实际样本。
- [git/git](profiles/git__git.md)：PR 1/3，正式 GitHub Release 0/3，接口错误 0。不足仅表示本方法取得的实际样本。
- [golang/go](profiles/golang__go.md)：PR 0/3，正式 GitHub Release 0/3，接口错误 0。不足仅表示本方法取得的实际样本。
- google/jax → jax-ml/jax，保留原样本标识与解析后的来源。
- [pytorch/pytorch](profiles/pytorch__pytorch.md)：PR 0/3，正式 GitHub Release 3/3，接口错误 0。不足仅表示本方法取得的实际样本。
