# golang/go

类别：语言与开发工具；状态：collected。

[仓库](https://github.com/golang/go) · [本地证据 JSON](../data/golang__go.json)

## 快照与身份

- 请求名称：golang/go；API 解析名称：golang/go。官方归属按样本维护组织与仓库声明核对，非第三方插件背书。
- 用途：The Go programming language
- 语言：Go；许可证：BSD-3-Clause；归档：False。
- Star：139283；Fork：22571；最近 push：2026-10-17T01:15:20Z。这些不是质量或使用人数指标。
- 默认分支：master；固定提交：`dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f`。
- 最早证据抓取：2026-10-17T16:16:12.143249+00:00；最后抓取：2026-10-17T16:20:29.682664+00:00；资料组装：2026-10-17T16:20:29.684170+00:00。逐端点时间见 JSON source_times。

## 内容、协作与维护

| 维度 | 文件证据或采样边界 |
| --- | --- |
| 文档入口 | [README.md](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/README.md)、[doc/README.md](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/doc/README.md) |
| 贡献与责任归属 | [CONTRIBUTING.md](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/CONTRIBUTING.md) |
| AI 指令与技能 | 所查范围未取得直接文件证据；其他位置未知 |
| 安全响应 | [SECURITY.md](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/SECURITY.md) |
| 包与构建配置 | 所查范围未取得直接文件证据；其他位置未知 |
| GitHub 工作流 | 目录列出 0 个，读取 0 个；配置存在不等于成功执行 |

以下为已读取文件的关键词候选信号，链接定位实际文本；不是逐条规则的语义证明。未命中仅表示采样范围未见，不代表仓库没有该能力。

| 维护信号 | 位置 |
| --- | --- |
| 测试命令候选 | 所查文件未命中；实际规则未知 |
| 格式与静态检查候选 | [.github/ISSUE_TEMPLATE/11-language-change.yml:146](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/ISSUE_TEMPLATE/11-language-change.yml#L146) |
| 生成代码提示 | 所查文件未命中；实际规则未知 |
| 自动发布配置候选 | 所查文件未命中；实际规则未知 |
| 工作流权限声明候选 | 所查文件未命中；实际规则未知 |
| 完整 SHA 固定的 Action 引用 | 所查文件未命中；实际规则未知 |
| 结构化提交约定候选 | 所查文件未命中；实际规则未知 |
| 安全响应入口候选 | [CONTRIBUTING.md:16](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/CONTRIBUTING.md#L16)、[SECURITY.md:1](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/SECURITY.md#L1)、[SECURITY.md:11](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/SECURITY.md#L11)、[SECURITY.md:13](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/SECURITY.md#L13) |

## 真实变更样本

默认分支提交样本：20/20；已合并 PR：0/3。
PR 按最近更新的已关闭且已合并到当前默认分支筛选，最多扫描 500 个；不代表最近合并时间排序，也不代表完整审查历史。

- [dfc6f7db](https://github.com/golang/go/commit/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f) cmd/compile: save and restore base.Pos some places where it&#x27;s set（2026-10-17T01:14:08Z）
- [29ceccda](https://github.com/golang/go/commit/29ceccda777f02095dc314d66464ba2a22492d12) cmd/internal/obj/loong64: optimize WORD instruction implementation（2026-10-17T00:58:27Z）
- [c3a068ee](https://github.com/golang/go/commit/c3a068eec992b5ae783abce1a9d03f617b671ea2) Revert &quot;internal/poll, runtime: isolate synchronous pipe I/O on Windows&quot;（2026-10-16T21:47:22Z）
- [8dfdca7c](https://github.com/golang/go/commit/8dfdca7cf2802057554f48c9d53ace41e3dc8a55) cmd/compile, simd/archsimd: add SVE mask FromCount constructors（2026-10-16T21:05:50Z）
- [c72492ee](https://github.com/golang/go/commit/c72492ee6dbb94a8e890be74b07f40d0a5acfd20) cmd/compile, simd/archsimd: add SVE ShiftAllLeft（2026-10-16T20:59:45Z）
- [3b3ca4b7](https://github.com/golang/go/commit/3b3ca4b7e6b99bdafdc0a9fee89e9bd616a2afa0) cmd/go: don&#x27;t let shared flags influence analyzer selection in std（2026-10-16T20:54:55Z）
- [61f71547](https://github.com/golang/go/commit/61f71547c919363251dbc7bff10dac3565bc6b5a) cmd/dist: add -artifacts-dir flag to dist test（2026-10-16T20:50:01Z）
- [b89302fe](https://github.com/golang/go/commit/b89302fe749fbb4ccf559b51975434ab830427bd) cmd/link: add a test for large symbol table in TestLargeReloc（2026-10-16T20:47:18Z）
- [8d781f99](https://github.com/golang/go/commit/8d781f9969c2c43286cdcaf0e237ca0abcc53e47) simd/archsimd/_gen: give SVE immediates a width and a range（2026-10-16T20:45:50Z）
- [a40a1665](https://github.com/golang/go/commit/a40a16659edabfbd059d450f078f58b3fa3e9b2f) simd/archsimd/_gen: key SVE arrangement rows by all their fields（2026-10-16T20:45:42Z）
- [efb714d0](https://github.com/golang/go/commit/efb714d031a7f59445aa6243f15eb00c79d11c8e) simd/archsimd: add SVE Float32s.ConvertToInt32（2026-10-16T20:45:27Z）
- [7eca4e7c](https://github.com/golang/go/commit/7eca4e7ce3d3cbf1080997245fb4754b341571a8) simd/archsimd/_gen: fold SVE predicated-only encodings per element width（2026-10-16T20:42:25Z）
- [387be259](https://github.com/golang/go/commit/387be2596257b51a0395bab693face5898824957) simd/archsimd: add SVE float ReduceMax（2026-10-16T20:42:12Z）
- [072b45cb](https://github.com/golang/go/commit/072b45cb3fcb255fdf9f7853c4435e39dede80f0) simd/internal/spec: add ReduceMax（2026-10-16T20:39:06Z）
- [dbd397ac](https://github.com/golang/go/commit/dbd397ac6d88e1e67b7cf7349f43688dcc22dcbc) cmd/compile, simd/archsimd: add SVE float ReduceSum（2026-10-16T20:36:20Z）
- [73c5f6f1](https://github.com/golang/go/commit/73c5f6f1827f4709e9e01336fb03d4fcd07b6445) cmd/go: keep go vet&#x27;s own tool flags in std packages（2026-10-16T20:17:51Z）
- [0564ffd5](https://github.com/golang/go/commit/0564ffd5f2e77883d39d369bd52fff66a253e8dd) cmd/compile: fix ICE on range over unsigned constant &gt;= 2^63 in clear loop（2026-10-16T20:00:55Z）
- [91d55590](https://github.com/golang/go/commit/91d55590e660b77c3f2b099a8cb15a2f166fa68b) cmd/compile: optimise bit tests with register shift values on riscv64（2026-10-16T20:00:38Z）
- [16d46baf](https://github.com/golang/go/commit/16d46baf6f96b0bd0c8fc1f4a32074f79966a6ed) runtime, testing: use a precise monotonic clock on Windows（2026-10-16T19:56:52Z）
- [53360921](https://github.com/golang/go/commit/53360921161c76348a30fe1cdb701e313710dc88) runtime: handle safe-point requests before executing goroutines（2026-10-16T19:56:35Z）

## 版本与发布

正式 GitHub Release 样本：0/3。从最多 100 个 API 创建顺序记录中过滤 draft/prerelease；不等于所有分支或包的最近发布时间排序。

最近标签：`weekly.2012-03-27`、`weekly.2012-03-22`、`weekly.2012-03-13`。
GitHub Release 不足时不推断未发布：包注册表、外部发布与标签式发布均需单独核对。

## 仓库展示与玩法

| 固定类别 | 观察位置 |
| --- | --- |
| 增长与活动 | 采样未见直接信号；未强行补齐 |
| 状态展示 | 采样未见直接信号；未强行补齐 |
| 项目门面 | [README.md:6](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/README.md#L6) |
| 快速体验 | 采样未见直接信号；未强行补齐 |
| 社区参与 | 采样未见直接信号；未强行补齐 |
| 项目故事 | 采样未见直接信号；未强行补齐 |

## 解释、建议与限制

维护建议：区分自举、编译、平台矩阵和插件生态；版本与发布方式依项目规则，不统一强制工具链。
本段是插件建议，不是该仓库明文要求。现有工作流、审查规则和展示内容应以链接原文及目标任务为准。
未知项包括有效分支保护、令牌实际权限、外部 CI、私有维护决策、历史 Star 数据；未访问不等于不存在。
读取成功 15 个文档/配置；工作流按名称优先采样至多 12 个，技能/插件目录各至多 3 个代表入口，大于 400 KB 文件跳过。

## 采集缺口

没有接口错误记录；这不表示没有上述采样限制。

## 文件来源清单

- [CONTRIBUTING.md](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/CONTRIBUTING.md)：35 行，blob `4cd76c29503d5dcee45240cd4de94e4f25c78d28`。
- [README.md](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/README.md)：42 行，blob `71c9d1dc2993880f38d227085d1b48c4070d1e85`。
- [SECURITY.md](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/SECURITY.md)：13 行，blob `e1718f0b012f7cea592027ae7574a6878f05f3fc`。
- [.github/CODE_OF_CONDUCT.md](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/CODE_OF_CONDUCT.md)：3 行，blob `2b4a5fccdaf12f98cf8e255affa28cfd7e6a784d`。
- [.github/ISSUE_TEMPLATE/00-bug.yml](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/ISSUE_TEMPLATE/00-bug.yml)：94 行，blob `5b0fda4950eb2e2cd8207635b1ac4ad88ce148b8`。
- [.github/ISSUE_TEMPLATE/01-pkgsite.yml](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/ISSUE_TEMPLATE/01-pkgsite.yml)：47 行，blob `aaf39b2928b32e721668e05e14b93dd19a45c764`。
- [.github/ISSUE_TEMPLATE/02-pkgsite-removal.yml](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/ISSUE_TEMPLATE/02-pkgsite-removal.yml)：42 行，blob `693f4999dcd47ae85938ffc363b72415ee74f5c9`。
- [.github/ISSUE_TEMPLATE/03-gopls.yml](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/ISSUE_TEMPLATE/03-gopls.yml)：71 行，blob `fd4c186cb89a47f7ff32d973f45e144c7e654421`。
- [.github/ISSUE_TEMPLATE/04-vuln.yml](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/ISSUE_TEMPLATE/04-vuln.yml)：52 行，blob `dd40af99c69eb22a0986dd4cb0d51a31446692d8`。
- [.github/ISSUE_TEMPLATE/10-proposal.yml](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/ISSUE_TEMPLATE/10-proposal.yml)：15 行，blob `d2a256c5aebfce203792a225d771a26370f84dba`。
- [.github/ISSUE_TEMPLATE/11-language-change.yml](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/ISSUE_TEMPLATE/11-language-change.yml)：165 行，blob `ac26ef6cb445bca0f6aff3e32ac8e3258198f787`。
- [.github/ISSUE_TEMPLATE/12-telemetry.yml](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/ISSUE_TEMPLATE/12-telemetry.yml)：30 行，blob `e072df260aaf634d490c178bca095d4e8429a6a4`。
- [.github/ISSUE_TEMPLATE/config.yml](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/ISSUE_TEMPLATE/config.yml)：5 行，blob `d6257daf2fa05f39872c49de51bb10763ba8fae7`。
- [.github/SUPPORT.md](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/.github/SUPPORT.md)：14 行，blob `d1fb277bc211da43ca59d9cff130d3f72a920bef`。
- [doc/README.md](https://github.com/golang/go/blob/dfc6f7db9bd75868ffb5cbc9501a2f4899122d2f/doc/README.md)：75 行，blob `b7aefc8d2c1e7badc95666dbdc0f3efab9364f0d`。
