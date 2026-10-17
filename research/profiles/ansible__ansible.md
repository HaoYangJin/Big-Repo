# ansible/ansible

类别：基础设施；状态：collected。

[仓库](https://github.com/ansible/ansible) · [本地证据 JSON](../data/ansible__ansible.json)

## 快照与身份

- 请求名称：ansible/ansible；API 解析名称：ansible/ansible。官方归属按样本维护组织与仓库声明核对，非第三方插件背书。
- 用途：Ansible is a radically simple IT automation platform that makes your applications and systems easier to deploy and maintain. Automate everything from code deployment to network configuration to cloud management, in a language that approaches plain English, using SSH, with no agents to install on remote systems. https://docs.ansible.com.
- 语言：Python；许可证：GPL-3.0；归档：False。
- Star：71002；Fork：24358；最近 push：2026-10-16T22:29:23Z。这些不是质量或使用人数指标。
- 默认分支：devel；固定提交：`f7319e09448e13fa2bc407a1afcd8990f47040fb`。
- 最早证据抓取：2026-10-17T16:14:53.912516+00:00；最后抓取：2026-10-17T16:17:15.111999+00:00；资料组装：2026-10-17T16:17:15.114507+00:00。逐端点时间见 JSON source_times。

## 内容、协作与维护

| 维度 | 文件证据或采样边界 |
| --- | --- |
| 文档入口 | [README.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md) |
| 贡献与责任归属 | [.github/CONTRIBUTING.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/CONTRIBUTING.md) |
| AI 指令与技能 | [AGENTS.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/AGENTS.md)、[CLAUDE.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/CLAUDE.md) |
| 安全响应 | [.github/SECURITY.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/SECURITY.md) |
| 包与构建配置 | [pyproject.toml](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/pyproject.toml) |
| GitHub 工作流 | 目录列出 0 个，读取 0 个；配置存在不等于成功执行 |

以下为已读取文件的关键词候选信号，链接定位实际文本；不是逐条规则的语义证明。未命中仅表示采样范围未见，不代表仓库没有该能力。

| 维护信号 | 位置 |
| --- | --- |
| 测试命令候选 | 所查文件未命中；实际规则未知 |
| 格式与静态检查候选 | 所查文件未命中；实际规则未知 |
| 生成代码提示 | 所查文件未命中；实际规则未知 |
| 自动发布配置候选 | 所查文件未命中；实际规则未知 |
| 工作流权限声明候选 | 所查文件未命中；实际规则未知 |
| 完整 SHA 固定的 Action 引用 | 所查文件未命中；实际规则未知 |
| 结构化提交约定候选 | 所查文件未命中；实际规则未知 |
| 安全响应入口候选 | [.github/ISSUE_TEMPLATE/config.yml:7](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/ISSUE_TEMPLATE/config.yml#L7)、[.github/SECURITY.md:1](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/SECURITY.md#L1)、[.github/SECURITY.md:3](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/SECURITY.md#L3)、[.github/SECURITY.md:34](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/SECURITY.md#L34) |

## 真实变更样本

默认分支提交样本：20/20；已合并 PR：3/3。
PR 按最近更新的已关闭且已合并到当前默认分支筛选，最多扫描 500 个；不代表最近合并时间排序，也不代表完整审查历史。

- [f7319e09](https://github.com/ansible/ansible/commit/f7319e09448e13fa2bc407a1afcd8990f47040fb) winrm - Remove config extras handling (#87655)（2026-10-16T22:29:22Z）
- [b458cf1c](https://github.com/ansible/ansible/commit/b458cf1c9d5189614e10e56256263597eb9ce3b0) pkg_mgr - use dnf as the default package manager on ROSA Linux (#87687)（2026-10-15T19:03:58Z）
- [14ae8474](https://github.com/ansible/ansible/commit/14ae8474978ca65ae9f9f71dff67f992b782291d) Add runtime deprecation for task failures inferred from a non-zero rc key in the result (#87696)（2026-10-14T23:34:36Z）
- [c8aad2b2](https://github.com/ansible/ansible/commit/c8aad2b2728beb50d4c5ff97f6977fb913ba2478) Remove Ubuntu 24.04 from controller tests (#87693)（2026-10-14T17:45:33Z）
- [7769a0b5](https://github.com/ansible/ansible/commit/7769a0b59580f0448e8c399d6bde6cdbdca5375a) Remove secret masking floor and ceiling (#87648)（2026-10-12T19:34:56Z）
- [c7750bc0](https://github.com/ansible/ansible/commit/c7750bc00a7e14173e54eaecc438ca5b839d30dc) ansible-test - Update base and default containers (#87673)（2026-10-12T18:24:29Z）
- [c3f68831](https://github.com/ansible/ansible/commit/c3f68831e571b3182024ee79c60ecbc6dff8d5b5) Remove double spaces in user-facing text (#87557)（2026-10-12T14:24:49Z）
- [fb75f60d](https://github.com/ansible/ansible/commit/fb75f60dd06e7c30c7a655cfe8c253d2e60c2839) tests: test empty string with from_yaml and from_yaml_all (#87639)（2026-10-12T13:43:29Z）
- [0d661975](https://github.com/ansible/ansible/commit/0d66197543ddbca1a7afa13da1df94bae70dd3ce) Ensure ansible-test-units-forked works without -v (#87662)（2026-10-09T17:15:58Z）
- [ed42c495](https://github.com/ansible/ansible/commit/ed42c495548e21cbc6fe71de14265926c152d046) ansible-galaxy collection install - fix validating paths before extraction (#87660)（2026-10-09T13:43:50Z）
- [5b1a96f0](https://github.com/ansible/ansible/commit/5b1a96f0fa54b54941904006744cb8200378e2f6) Redact content if any error has show_content=False (#87548)（2026-10-08T20:39:34Z）
- [be41e1d4](https://github.com/ansible/ansible/commit/be41e1d46792e9c6f85ee2547d6d4a6b027cf29b) cron module: Add configurable cron executable (#87575)（2026-10-08T14:36:01Z）
- [bf2610eb](https://github.com/ansible/ansible/commit/bf2610eb39b066994bb457f95359907aef0ae972) Fix crash on no_log options with non-string defaults (#87624)（2026-10-07T00:59:14Z）
- [a77b8a7a](https://github.com/ansible/ansible/commit/a77b8a7ac60b5e20e64a8030b8499d1292d18f13) iptables tests: ensure kernel-modules-extra matches running kernel (#87631)（2026-10-06T22:53:21Z）
- [be0fd3b1](https://github.com/ansible/ansible/commit/be0fd3b10c00bf604b3a8bb519a5960074f2e26d) service - Map restart to onerestart for FreeBSD #84793 (#87585)（2026-10-02T21:01:25Z）
- [abf5bf59](https://github.com/ansible/ansible/commit/abf5bf59a229e0df2e15a421a5eff83a7b8e3796) sudo become plugin - handle sudo-rs i18n (#86964)（2026-09-30T14:33:30Z）
- [a900ea9d](https://github.com/ansible/ansible/commit/a900ea9d0c3665d4013d305dabe6d0af2c3231f8) mask_url, deal with unparsable url (#87562)（2026-09-29T16:13:53Z）
- [00b36d9a](https://github.com/ansible/ansible/commit/00b36d9ac630b5aaf03d143ef8c96e539fad2912) Drop support for Python 3.9 (#87582)（2026-09-28T17:59:56Z）
- [f491c35c](https://github.com/ansible/ansible/commit/f491c35c7026dfd8c20b7d4e44ea5e5e1d9d5e83) ansible-connection, ensure proper permission for persistent dir (#87574)（2026-09-28T15:22:53Z）
- [7ec731bf](https://github.com/ansible/ansible/commit/7ec731bfd2dbfd7b5a11ac53bf32ad2a4bf57ed4) Create mask_object method for secret redaction (#87559)（2026-09-24T19:56:20Z）

### [PR #87655](https://github.com/ansible/ansible/pull/87655) winrm - Remove config extras handling
合并：2026-10-16T22:29:23Z；merge SHA：`f7319e09448e13fa2bc407a1afcd8990f47040fb`；公开 review 状态：APPROVED。
变更文件：3 个（单页上限 100，可能截断：False）。
涉及路径：`changelogs/fragments/winrm-extras.yml`、`lib/ansible/plugins/connection/winrm.py`、`test/units/plugins/connection/test_winrm.py`。
未取得该 head/merge SHA 的 GitHub Actions 运行；外部 CI、删除或过期记录均未知。

### [PR #87585](https://github.com/ansible/ansible/pull/87585) service - Map restart to onerestart for FreeBSD #84793
合并：2026-10-02T21:01:26Z；merge SHA：`be0fd3b10c00bf604b3a8bb519a5960074f2e26d`；公开 review 状态：CHANGES_REQUESTED, CHANGES_REQUESTED, COMMENTED, COMMENTED, COMMENTED, COMMENTED, APPROVED, APPROVED, COMMENTED, COMMENTED。
变更文件：3 个（单页上限 100，可能截断：False）。
涉及路径：`changelogs/fragments/84793-map-restart-to-onerestart-for-freebsd.yml`、`lib/ansible/modules/service.py`、`test/integration/targets/service/tasks/tests.yml`。
未取得该 head/merge SHA 的 GitHub Actions 运行；外部 CI、删除或过期记录均未知。

### [PR #87687](https://github.com/ansible/ansible/pull/87687) pkg_mgr - use dnf as the default package manager on ROSA Linux
合并：2026-10-15T19:03:59Z；merge SHA：`b458cf1c9d5189614e10e56256263597eb9ce3b0`；公开 review 状态：COMMENTED, COMMENTED, DISMISSED, COMMENTED, COMMENTED, APPROVED。
变更文件：3 个（单页上限 100，可能截断：False）。
涉及路径：`changelogs/fragments/pkg-mgr-rosa-mos-dnf.yml`、`lib/ansible/module_utils/facts/system/pkg_mgr.py`、`test/units/module_utils/facts/system/test_pkg_mgr.py`。
未取得该 head/merge SHA 的 GitHub Actions 运行；外部 CI、删除或过期记录均未知。

## 版本与发布

正式 GitHub Release 样本：3/3。从最多 100 个 API 创建顺序记录中过滤 draft/prerelease；不等于所有分支或包的最近发布时间排序。

- [v2.21.5](https://github.com/ansible/ansible/releases/tag/v2.21.5)：2026-10-05T15:11:41Z；提交 `3d36adf9a541aba1ed5f37aa124170f1f2df0a65`；资产 0 个。
- [v2.20.10](https://github.com/ansible/ansible/releases/tag/v2.20.10)：2026-10-05T15:10:10Z；提交 `4e55d1cfd9f8d1aac5edc2ad0a535b68a238659b`；资产 0 个。
- [v2.19.14](https://github.com/ansible/ansible/releases/tag/v2.19.14)：2026-10-05T15:08:52Z；提交 `1cfd790f10476c40e129b2ada615e00fd11c9ec9`；资产 0 个。
最近标签：`v2.22.0rc1`、`v2.22.0b2`、`v2.22.0b1`。
GitHub Release 不足时不推断未发布：包注册表、外部发布与标签式发布均需单独核对。

## 仓库展示与玩法

| 固定类别 | 观察位置 |
| --- | --- |
| 增长与活动 | 采样未见直接信号；未强行补齐 |
| 状态展示 | [README.md:1](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L1)、[README.md:2](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L2)、[README.md:3](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L3)、[README.md:4](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L4) |
| 项目门面 | [README.md:1](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L1)、[README.md:2](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L2)、[README.md:3](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L3)、[README.md:4](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L4) |
| 快速体验 | 采样未见直接信号；未强行补齐 |
| 社区参与 | [README.md:87](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L87)、[README.md:89](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L89)、[README.md:90](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md#L90) |
| 项目故事 | [.github/SECURITY.md:23](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/SECURITY.md#L23) |

## 解释、建议与限制

维护建议：优先核对组件责任、集成环境和升级兼容；本地单元测试不代表集群或生产部署验证。
本段是插件建议，不是该仓库明文要求。现有工作流、审查规则和展示内容应以链接原文及目标任务为准。
未知项包括有效分支保护、令牌实际权限、外部 CI、私有维护决策、历史 Star 数据；未访问不等于不存在。
读取成功 22 个文档/配置；工作流按名称优先采样至多 12 个，技能/插件目录各至多 3 个代表入口，大于 400 KB 文件跳过。

## 采集缺口

没有接口错误记录；这不表示没有上述采样限制。

## 文件来源清单

- [AGENTS.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/AGENTS.md)：175 行，blob `1d6361df34d107f77178f332b6f773e348be5a0a`。
- [CLAUDE.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/CLAUDE.md)：3 行，blob `a076ce07bdbb576137f2575a894d8277e65422a5`。
- [README.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/README.md)：107 行，blob `ed464e118bf451b1274cee7994d0b66f1774c632`。
- [pyproject.toml](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/pyproject.toml)：114 行，blob `37b943ec151156536769b3b7852bd24208142fab`。
- [.github/CODE_OF_CONDUCT.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/CODE_OF_CONDUCT.md)：3 行，blob `0164155b81025416095f31a4732098ec238e6476`。
- [.github/CONTRIBUTING.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/CONTRIBUTING.md)：78 行，blob `fc15ea5dfc2f5a29da810ce5b79b2d969f3ec6af`。
- [.github/ISSUE_TEMPLATE.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/ISSUE_TEMPLATE.md)：1 行，blob `f1f99bc6227eca51140067edd38e87f79c81556b`。
- [.github/ISSUE_TEMPLATE/bug_report.yml](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/ISSUE_TEMPLATE/bug_report.yml)：251 行，blob `4f8efe4a3e16095b4369a11e0794df3ae6e86aea`。
- [.github/ISSUE_TEMPLATE/config.yml](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/ISSUE_TEMPLATE/config.yml)：26 行，blob `140f479aed07f8e7448b7c546a5696210aab4589`。
- [.github/ISSUE_TEMPLATE/documentation_report.yml](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/ISSUE_TEMPLATE/documentation_report.yml)：203 行，blob `c5ceebad7b97905d35aa380bf5470424a031fda0`。
- [.github/ISSUE_TEMPLATE/feature_request.yml](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/ISSUE_TEMPLATE/feature_request.yml)：176 行，blob `c8529dc6a7e578e7ee493623a0f962d209a7334e`。
- [.github/ISSUE_TEMPLATE/internal_issue.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/ISSUE_TEMPLATE/internal_issue.md)：9 行，blob `4ba09737904502182852e7ebda93bc0a6a7c2de1`。
- [.github/ISSUE_TEMPLATE/pre_release.yml](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/ISSUE_TEMPLATE/pre_release.yml)：42 行，blob `80f10eb845d712c001bc2432979aacb87e812650`。
- [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/PULL_REQUEST_TEMPLATE.md)：1 行，blob `c8ecb720058ad7aef6f583af35c92cfa600f1c97`。
- [.github/PULL_REQUEST_TEMPLATE/Bug fix.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/PULL_REQUEST_TEMPLATE/Bug%20fix.md)：9 行，blob `3ad5e0cff2b66b86e51d548af78ffe755c8b3875`。
- [.github/PULL_REQUEST_TEMPLATE/Documentation change.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/PULL_REQUEST_TEMPLATE/Documentation%20change.md)：9 行，blob `e0280ea016a3c9627626c714e7b9a1c6ecfbc564`。
- [.github/PULL_REQUEST_TEMPLATE/New feature.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/PULL_REQUEST_TEMPLATE/New%20feature.md)：9 行，blob `bd56e0211644973dbbef26a3fbaab5fdcc6d2c9c`。
- [.github/PULL_REQUEST_TEMPLATE/PULL_REQUEST_TEMPLATE.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/PULL_REQUEST_TEMPLATE/PULL_REQUEST_TEMPLATE.md)：1 行，blob `3df4f489ad7a900e16a3480f65837ce0852cb6af`。
- [.github/PULL_REQUEST_TEMPLATE/Tests.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/PULL_REQUEST_TEMPLATE/Tests.md)：9 行，blob `80eb3c6ab021058be26d432571592f7f25535cc3`。
- [.github/PULL_REQUEST_TEMPLATE/Unclear purpose or motivation.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/PULL_REQUEST_TEMPLATE/Unclear%20purpose%20or%20motivation.md)：14 行，blob `baed1c6c83b6747be188056010dc591c13e8beb8`。
- [.github/RELEASE_NAMES.txt](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/RELEASE_NAMES.txt)：23 行，blob `9be45f19cf8727906894076a27614ae336b39bd4`。
- [.github/SECURITY.md](https://github.com/ansible/ansible/blob/f7319e09448e13fa2bc407a1afcd8990f47040fb/.github/SECURITY.md)：43 行，blob `5db130b4bdb5ea13c583e02f7be267b93e31e58c`。
