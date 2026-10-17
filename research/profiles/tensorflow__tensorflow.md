# tensorflow/tensorflow

类别：模型与机器学习；状态：collected。

[仓库](https://github.com/tensorflow/tensorflow) · [本地证据 JSON](../data/tensorflow__tensorflow.json)

## 快照与身份

- 请求名称：tensorflow/tensorflow；API 解析名称：tensorflow/tensorflow。官方归属按样本维护组织与仓库声明核对，非第三方插件背书。
- 用途：An Open Source Machine Learning Framework for Everyone
- 语言：C++；许可证：Apache-2.0；归档：False。
- Star：201076；Fork：79641；最近 push：2026-10-17T15:52:17Z。这些不是质量或使用人数指标。
- 默认分支：master；固定提交：`d34b7e701f320d4a265f67357bd6a3a53a4c1ccf`。
- 最早证据抓取：2026-10-17T16:09:34.357893+00:00；最后抓取：2026-10-17T16:17:01.821547+00:00；资料组装：2026-10-17T16:17:01.824188+00:00。逐端点时间见 JSON source_times。

## 内容、协作与维护

| 维度 | 文件证据或采样边界 |
| --- | --- |
| 文档入口 | [README.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/README.md) |
| 贡献与责任归属 | [CODEOWNERS](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/CODEOWNERS)、[CONTRIBUTING.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/CONTRIBUTING.md) |
| AI 指令与技能 | 所查范围未取得直接文件证据；其他位置未知 |
| 安全响应 | [SECURITY.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/SECURITY.md) |
| 包与构建配置 | 所查范围未取得直接文件证据；其他位置未知 |
| GitHub 工作流 | 目录列出 18 个，读取 12 个；配置存在不等于成功执行 |

以下为已读取文件的关键词候选信号，链接定位实际文本；不是逐条规则的语义证明。未命中仅表示采样范围未见，不代表仓库没有该能力。

| 维护信号 | 位置 |
| --- | --- |
| 测试命令候选 | 所查文件未命中；实际规则未知 |
| 格式与静态检查候选 | 所查文件未命中；实际规则未知 |
| 生成代码提示 | 所查文件未命中；实际规则未知 |
| 自动发布配置候选 | 所查文件未命中；实际规则未知 |
| 工作流权限声明候选 | [.github/workflows/arm-ci-extended-cpp.yml:25](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-ci-extended-cpp.yml#L25)、[.github/workflows/arm-ci-extended.yml:25](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-ci-extended.yml#L25)、[.github/workflows/arm-ci.yml:23](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-ci.yml#L23)、[.github/workflows/ci-build.yml:23](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/ci-build.yml#L23) |
| 完整 SHA 固定的 Action 引用 | [.github/workflows/arm-ci-extended-cpp.yml:53](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-ci-extended-cpp.yml#L53)、[.github/workflows/arm-ci-extended-cpp.yml:58](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-ci-extended-cpp.yml#L58)、[.github/workflows/arm-ci-extended.yml:54](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-ci-extended.yml#L54)、[.github/workflows/arm-ci-extended.yml:59](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-ci-extended.yml#L59) |
| 结构化提交约定候选 | 所查文件未命中；实际规则未知 |
| 安全响应入口候选 | [SECURITY.md:147](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/SECURITY.md#L147) |

## 真实变更样本

默认分支提交样本：20/20；已合并 PR：3/3。
PR 按最近更新的已关闭且已合并到当前默认分支筛选，最多扫描 500 个；不代表最近合并时间排序，也不代表完整审查历史。

- [d34b7e70](https://github.com/tensorflow/tensorflow/commit/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf) Refactor CostModel into extensible base and introduce DenseCostModel（2026-10-17T15:52:09Z）
- [af59db94](https://github.com/tensorflow/tensorflow/commit/af59db942b61f68d2e320be3249a1c2339adb41e) Automated Code Change（2026-10-17T13:17:29Z）
- [8329f1bc](https://github.com/tensorflow/tensorflow/commit/8329f1bc2bdffaecb9ae935aec723f89da67a50e) Lower `lax.exp2_p` and `lax.log2_p` directly to `stablehlo.exp2` and `stablehlo.log2`（2026-10-17T10:21:09Z）
- [9223b754](https://github.com/tensorflow/tensorflow/commit/9223b75468a239ec00058eead2b9b8206ccbaebe) [XLA] Remove deprecated HloPassInterface::Run(std::unique_ptr&lt;HloModule&gt;&amp;).（2026-10-17T08:11:16Z）
- [fceefffb](https://github.com/tensorflow/tensorflow/commit/fceefffb2c92b346b7e1178fb5f87bcc39a11c3a) Merge pull request #128629 from vishwakt:fix-xla-nms-threshold-dtype（2026-10-17T08:01:39Z）
- [f83e85ba](https://github.com/tensorflow/tensorflow/commit/f83e85bae0b39efe1127e211cdd20999dde3a286) Merge pull request #123572 from madib06ops:uncompress-zero-element-component（2026-10-17T07:47:12Z）
- [b9b04b17](https://github.com/tensorflow/tensorflow/commit/b9b04b174ab779066680ea3fe65f056e5f88854e) [XLA:TSL] Deduplicate Eigen spatial convolution contraction mappers across alignment and contiguity parameters（2026-10-17T07:37:00Z）
- [f601a92c](https://github.com/tensorflow/tensorflow/commit/f601a92cdb5b7a38d85d7733b655f1215ae1d8bc) Clean up dedup_meshes.cc and preserve reductionOp in replaceAxesInSharding.（2026-10-17T06:06:45Z）
- [ec591b48](https://github.com/tensorflow/tensorflow/commit/ec591b48038d4e5f0a2123d5216dc9439e54eb2a) Fix two problems in handling sub axes in rewriteReplicaGroupAttr.（2026-10-17T04:54:44Z）
- [0bb599ee](https://github.com/tensorflow/tensorflow/commit/0bb599ee9143fea0ee0d4469d07ca62eaf9a5375) Copy host&lt;-&gt;device transfers directly under GPU Confidential Computing.（2026-10-17T03:32:57Z）
- [cae52ab7](https://github.com/tensorflow/tensorflow/commit/cae52ab735293bcf2743802662108207ee86402e) Wait for receiver allocation sync points before cross-host GPU recv.（2026-10-17T01:26:52Z）
- [6d648305](https://github.com/tensorflow/tensorflow/commit/6d648305df6b05e4d62651f0ca1fead0654374dd) [XLA:CPU] Fold sin(-x) and cos(-x) before intrinsic lowering.（2026-10-17T00:43:06Z）
- [3b5883f4](https://github.com/tensorflow/tensorflow/commit/3b5883f49798646a739d15961856dd4a1314aa53) Use relative tolerance in `DefaultSchedulerCore::AddOccupierToResource` latency check.（2026-10-17T00:28:38Z）
- [ae7e665e](https://github.com/tensorflow/tensorflow/commit/ae7e665e5f29fda9ed1548d523ca7f16c0121e2c) Add `spanner_fdo_key` field to `SparseCoreTableLayout` proto for non-abbreviated Spanner FDO table keys.（2026-10-17T00:13:17Z）
- [883ec7a5](https://github.com/tensorflow/tensorflow/commit/883ec7a57c2ad3a7eb2bb344bdc8553af940bd35) Integrate LLVM at llvm/llvm-project@4fa92e8e51e6（2026-10-17T00:09:30Z）
- [25ca0f0b](https://github.com/tensorflow/tensorflow/commit/25ca0f0b536e4ccfe1e3151193f46e66a4825d32) Add protobuf serialization and deserialization to tensorflow::RequestCost.（2026-10-17T00:01:46Z）
- [77ab63cf](https://github.com/tensorflow/tensorflow/commit/77ab63cfaae1589716aacfc7e191de0e6edbac8f) [XLA Highway] Switch XLA transpose kernels to Highway &amp; clean up legacy intrinsics（2026-10-16T23:49:27Z）
- [55310b93](https://github.com/tensorflow/tensorflow/commit/55310b93b77ae7741a26b9b8a463e2b8ef11f45e) Add an executable checks option to deserialization and add LaunchOnDevice.（2026-10-16T23:27:26Z）
- [f6a32b7a](https://github.com/tensorflow/tensorflow/commit/f6a32b7a75fe2e9c61ef4d8f7be75d115a201876) Roll forward of &quot;[Mosaic] Fix tpu.memref_squeeze...&quot; with relaxed verifier（2026-10-16T23:22:47Z）
- [9dd1241c](https://github.com/tensorflow/tensorflow/commit/9dd1241c2a15417ac0c9eb3940f67bd7639b4646) [XLA Highway] Add 8x32 byte transpose microkernel（2026-10-16T22:49:27Z）

### [PR #128629](https://github.com/tensorflow/tensorflow/pull/128629) Convert NMS thresholds to the boxes&#x27; type in XLA
合并：2026-10-17T08:02:04Z；merge SHA：`fceefffb2c92b346b7e1178fb5f87bcc39a11c3a`；公开 review 状态：COMMENTED, COMMENTED, CHANGES_REQUESTED, APPROVED, CHANGES_REQUESTED, APPROVED, CHANGES_REQUESTED, APPROVED。
变更文件：2 个（单页上限 100，可能截断：False）。
涉及路径：`tensorflow/compiler/tests/image_ops_test.py`、`tensorflow/compiler/tf2xla/kernels/image_ops.cc`。
- [运行 39015844333](https://github.com/tensorflow/tensorflow/actions/runs/39015844333) Creates a GitHub Issue when a PR Rolled back via Commit to Master；事件 push；状态 completed/skipped；工作流 `.github/workflows/issue-on-pr-rollback.yml`。
- [运行 39015844296](https://github.com/tensorflow/tensorflow/actions/runs/39015844296) Scorecards supply-chain security；事件 push；状态 completed/success；工作流 `.github/workflows/scorecards-analysis.yml`。
- [运行 39015844204](https://github.com/tensorflow/tensorflow/actions/runs/39015844204) Push on master；事件 dynamic；状态 completed/success；工作流 `dynamic/github-code-scanning/codeql`。
- [运行 38820934357](https://github.com/tensorflow/tensorflow/actions/runs/38820934357) Gemini PR Review；事件 pull_request；状态 completed/skipped；工作流 `.github/workflows/gemini.yml`。
- [运行 38315248689](https://github.com/tensorflow/tensorflow/actions/runs/38315248689) CI；事件 pull_request；状态 completed/success；工作流 `.github/workflows/ci-build.yml`。
- [运行 38315248468](https://github.com/tensorflow/tensorflow/actions/runs/38315248468) PyLint；事件 pull_request；状态 completed/success；工作流 `.github/workflows/pylint-presubmit.yml`。
- [运行 38315248240](https://github.com/tensorflow/tensorflow/actions/runs/38315248240) License Check；事件 pull_request；状态 completed/success；工作流 `.github/workflows/check_license.yml`。
- [运行 38315244065](https://github.com/tensorflow/tensorflow/actions/runs/38315244065) GitHub Actions Scan；事件 pull_request_target；状态 completed/success；工作流 `.github/workflows/github_actions_scan.yml`。

### [PR #123572](https://github.com/tensorflow/tensorflow/pull/123572) reject zero-element non-memcpyable components in UncompressElement
合并：2026-10-17T07:47:35Z；merge SHA：`f83e85bae0b39efe1127e211cdd20999dde3a286`；公开 review 状态：COMMENTED, COMMENTED, APPROVED, DISMISSED, CHANGES_REQUESTED, APPROVED, APPROVED, CHANGES_REQUESTED, CHANGES_REQUESTED, CHANGES_REQUESTED, CHANGES_REQUESTED, APPROVED, CHANGES_REQUESTED。
变更文件：2 个（单页上限 100，可能截断：False）。
涉及路径：`tensorflow/core/data/compression_utils.cc`、`tensorflow/core/data/compression_utils_test.cc`。
- [运行 39014957364](https://github.com/tensorflow/tensorflow/actions/runs/39014957364) Creates a GitHub Issue when a PR Rolled back via Commit to Master；事件 push；状态 completed/skipped；工作流 `.github/workflows/issue-on-pr-rollback.yml`。
- [运行 39014957314](https://github.com/tensorflow/tensorflow/actions/runs/39014957314) Scorecards supply-chain security；事件 push；状态 completed/success；工作流 `.github/workflows/scorecards-analysis.yml`。
- [运行 39014957182](https://github.com/tensorflow/tensorflow/actions/runs/39014957182) Push on master；事件 dynamic；状态 completed/success；工作流 `dynamic/github-code-scanning/codeql`。
- [运行 37732328306](https://github.com/tensorflow/tensorflow/actions/runs/37732328306) Gemini PR Review；事件 pull_request；状态 completed/skipped；工作流 `.github/workflows/gemini.yml`。
- [运行 37732327657](https://github.com/tensorflow/tensorflow/actions/runs/37732327657) Gemini PR Review；事件 pull_request；状态 completed/skipped；工作流 `.github/workflows/gemini.yml`。
- [运行 37725811244](https://github.com/tensorflow/tensorflow/actions/runs/37725811244) License Check；事件 pull_request；状态 completed/success；工作流 `.github/workflows/check_license.yml`。
- [运行 37725811358](https://github.com/tensorflow/tensorflow/actions/runs/37725811358) CI；事件 pull_request；状态 completed/success；工作流 `.github/workflows/ci-build.yml`。
- [运行 37725807805](https://github.com/tensorflow/tensorflow/actions/runs/37725807805) GitHub Actions Scan；事件 pull_request_target；状态 completed/success；工作流 `.github/workflows/github_actions_scan.yml`。

### [PR #129161](https://github.com/tensorflow/tensorflow/pull/129161) Add `spanner_fdo_key` field to `SparseCoreTableLayout` proto for non-abbreviated Spanner FDO table keys.
合并：2026-10-17T00:13:30Z；merge SHA：`ae7e665e5f29fda9ed1548d523ca7f16c0121e2c`；公开 review 状态：采样未取得。
变更文件：1 个（单页上限 100，可能截断：False）。
涉及路径：`tensorflow/core/tpu/kernels/sparse_core_layout.proto`。
- [运行 38985368775](https://github.com/tensorflow/tensorflow/actions/runs/38985368775) Creates a GitHub Issue when a PR Rolled back via Commit to Master；事件 push；状态 completed/skipped；工作流 `.github/workflows/issue-on-pr-rollback.yml`。
- [运行 38985368773](https://github.com/tensorflow/tensorflow/actions/runs/38985368773) Scorecards supply-chain security；事件 push；状态 completed/success；工作流 `.github/workflows/scorecards-analysis.yml`。
- [运行 38985368185](https://github.com/tensorflow/tensorflow/actions/runs/38985368185) CI；事件 pull_request；状态 completed/success；工作流 `.github/workflows/ci-build.yml`。
- [运行 38985368154](https://github.com/tensorflow/tensorflow/actions/runs/38985368154) License Check；事件 pull_request；状态 completed/success；工作流 `.github/workflows/check_license.yml`。
- [运行 38985367712](https://github.com/tensorflow/tensorflow/actions/runs/38985367712) Push on master；事件 dynamic；状态 completed/success；工作流 `dynamic/github-code-scanning/codeql`。
- [运行 38985365730](https://github.com/tensorflow/tensorflow/actions/runs/38985365730) GitHub Actions Scan；事件 pull_request_target；状态 completed/success；工作流 `.github/workflows/github_actions_scan.yml`。
- [运行 38985364213](https://github.com/tensorflow/tensorflow/actions/runs/38985364213) PR #129161；事件 dynamic；状态 completed/success；工作流 `dynamic/github-code-scanning/codeql`。

## 版本与发布

正式 GitHub Release 样本：3/3。从最多 100 个 API 创建顺序记录中过滤 draft/prerelease；不等于所有分支或包的最近发布时间排序。

- [v2.21.0](https://github.com/tensorflow/tensorflow/releases/tag/v2.21.0)：2026-03-06T19:48:15Z；提交 `a481b10260dfdf833a1b16007eead49c1d7febf3`；资产 0 个。
  - [关联运行 22779376435](https://github.com/tensorflow/tensorflow/actions/runs/22779376435)：cffconvert，push，success。同 SHA 关联不证明由该 Release 触发。
  - [关联运行 22690380026](https://github.com/tensorflow/tensorflow/actions/runs/22690380026)：Push on r2.21，dynamic，success。同 SHA 关联不证明由该 Release 触发。
- [v2.19.1](https://github.com/tensorflow/tensorflow/releases/tag/v2.19.1)：2025-08-13T17:45:03Z；提交 `f4247ebb6f9e7421f38c3f01a9a5d5cd54bd24fd`；资产 0 个。
- [v2.20.0](https://github.com/tensorflow/tensorflow/releases/tag/v2.20.0)：2025-08-13T17:45:14Z；提交 `72fbba3d20f4616d7312b5e2b7f79daf6e82f2fa`；资产 0 个。
最近标签：`v2.22.0-rc0`、`v2.21.0`、`v2.21.0-rc1`。
GitHub Release 不足时不推断未发布：包注册表、外部发布与标签式发布均需单独核对。

## 仓库展示与玩法

| 固定类别 | 观察位置 |
| --- | --- |
| 增长与活动 | 采样未见直接信号；未强行补齐 |
| 状态展示 | [README.md:5](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/README.md#L5)、[README.md:6](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/README.md#L6)、[README.md:12](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/README.md#L12)、[README.md:13](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/README.md#L13) |
| 项目门面 | [CONTRIBUTING.md:18](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/CONTRIBUTING.md#L18)、[CONTRIBUTING.md:74](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/CONTRIBUTING.md#L74)、[README.md:2](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/README.md#L2)、[README.md:5](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/README.md#L5) |
| 快速体验 | [.github/ISSUE_TEMPLATE/tflite-converter-issue.md:20](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/ISSUE_TEMPLATE/tflite-converter-issue.md#L20)、[.github/ISSUE_TEMPLATE/tflite-converter-issue.md:21](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/ISSUE_TEMPLATE/tflite-converter-issue.md#L21) |
| 社区参与 | [CONTRIBUTING.md:107](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/CONTRIBUTING.md#L107)、[README.md:151](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/README.md#L151) |
| 项目故事 | [SECURITY.md:66](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/SECURITY.md#L66) |

## 解释、建议与限制

维护建议：确认硬件、模型权重、测试矩阵与可用环境；没有运行硬件测试时明确未验证，不能用文档检查替代。
本段是插件建议，不是该仓库明文要求。现有工作流、审查规则和展示内容应以链接原文及目标任务为准。
未知项包括有效分支保护、令牌实际权限、外部 CI、私有维护决策、历史 Star 数据；未访问不等于不存在。
读取成功 24 个文档/配置；工作流按名称优先采样至多 12 个，技能/插件目录各至多 3 个代表入口，大于 400 KB 文件跳过。

## 采集缺口

没有接口错误记录；这不表示没有上述采样限制。

## 文件来源清单

- [CODEOWNERS](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/CODEOWNERS)：18 行，blob `a574493352c31d88a968a0dfa2f7b806bbf96db2`。
- [CODE_OF_CONDUCT.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/CODE_OF_CONDUCT.md)：79 行，blob `e5203a7cf2286eeb309ce4ea099c41fb2f872c65`。
- [CONTRIBUTING.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/CONTRIBUTING.md)：375 行，blob `1a1f2350cd69c1e7e29347e7df55e6fbb1c1a9b8`。
- [README.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/README.md)：168 行，blob `2ada91b134b2bc6daa60ca6265f1290f38a748c1`。
- `RELEASE.md`：skipped-size。
- [SECURITY.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/SECURITY.md)：187 行，blob `4d52d02cb53d17ecbd16a0e6ce3cae5e6e7331ca`。
- [.github/ISSUE_TEMPLATE/config.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/ISSUE_TEMPLATE/config.yml)：16 行，blob `531e35ed48afcb0d5f78bf56544fe3fbb25b731d`。
- [.github/ISSUE_TEMPLATE/tensorflow_issue_template.yaml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/ISSUE_TEMPLATE/tensorflow_issue_template.yaml)：141 行，blob `a39d5b2a956a0d1b1f28c8cf052b5cbf37b5d980`。
- [.github/ISSUE_TEMPLATE/tflite-converter-issue.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/ISSUE_TEMPLATE/tflite-converter-issue.md)：47 行，blob `70be52989048c21e3523fd4318f3827408177b5f`。
- [.github/ISSUE_TEMPLATE/tflite-in-play-services.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/ISSUE_TEMPLATE/tflite-in-play-services.md)：23 行，blob `429b842a2d05fba7059d5a9b1a6569f024c003cc`。
- [.github/ISSUE_TEMPLATE/tflite-op-request.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/ISSUE_TEMPLATE/tflite-op-request.md)：30 行，blob `4f1e60b553abeb5248b47f591f7f7936d1df0afb`。
- [.github/ISSUE_TEMPLATE/tflite-other.md](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/ISSUE_TEMPLATE/tflite-other.md)：62 行，blob `8b8246f2b72afc60c79865cb09a9784f30ecd7a4`。
- [.github/dependabot.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/dependabot.yml)：45 行，blob `dc2cd714664a0b420d649a140dd717b94e9cb78f`。
- [.github/workflows/arm-ci-extended-cpp.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-ci-extended-cpp.yml)：64 行，blob `06a6e9bdf4113a60d6ef846f4fcd2c40de4a3b22`。
- [.github/workflows/arm-ci-extended.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-ci-extended.yml)：65 行，blob `e67407140e00171cbd3b2c417cabdb0b96d680ec`。
- [.github/workflows/arm-ci.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-ci.yml)：55 行，blob `9189e14bc79bc4a6ebde4dd80c68b7d0738e7e96`。
- [.github/workflows/ci-build.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/ci-build.yml)：61 行，blob `0af4c3a03ee0cab3fabf428f0269b32d60874729`。
- [.github/workflows/release-branch-cherrypick.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/release-branch-cherrypick.yml)：71 行，blob `9cc30dd9b3073d7fbb75328651681b50afa00693`。
- [.github/workflows/arm-cd.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/arm-cd.yml)：71 行，blob `58b4908e1c1509d1d0bfe886ae3aaa4ad39e3548`。
- [.github/workflows/build-reusable.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/build-reusable.yml)：71 行，blob `e330cf1d099e020a7c3494b459739fc3ee1e03c5`。
- [.github/workflows/cffconvert.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/cffconvert.yml)：38 行，blob `55c95389f5161d886dcafaac02f2d99f13dbc93b`。
- [.github/workflows/check_license.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/check_license.yml)：57 行，blob `b810e78633137d0e2e69ff9e35a7c8b97e8a3b64`。
- [.github/workflows/create_issue.js](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/create_issue.js)：64 行，blob `eca20953f8484adad41f390347407339bdd573a0`。
- [.github/workflows/gemini.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/gemini.yml)：39 行，blob `28cff13f49e2f192ad0f65af2972c1f987f10104`。
- [.github/workflows/issue-on-pr-rollback.yml](https://github.com/tensorflow/tensorflow/blob/d34b7e701f320d4a265f67357bd6a3a53a4c1ccf/.github/workflows/issue-on-pr-rollback.yml)：43 行，blob `4795c11da8806163a37765b904df7cbfce6279cd`。
