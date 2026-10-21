# 研究方法与证据边界

## 范围

这是针对明确列出的 60 个官方组织维护仓库的分层案例研究，不是 GitHub 全量调查或统计代表性抽样。六类各 10 个，样本在研究开始前固定于 roster.json。
“官方”表示指定项目的维护组织与项目仓库身份，不表示相关公司认可本插件。API 返回的 owner、canonical full_name、仓库用途和文档声明用于交叉核对；迁移、镜像、反馈仓库和归档状态必须单列。

## 获取方式

使用 GitHub REST 只读接口和已有 gh 登录，不收集令牌。按默认分支首次取得的 20 个提交之首固定文档 SHA，再读取根目录、.github、docs/doc 中相关说明与配置。
工作流目录完整列名，读取上限 12 个，优先名称涉及 release/publish/test/ci/security/dependency 的文件；技能和插件目录分别读取最多 3 个代表入口。
单个大于 400 KB 的文件跳过，GitHub 单响应大于 12 MB 停止并记缺口。此范围不会穷尽所有包、嵌套目录、CI 平台或维护流程。

PR：按更新时间降序读取已关闭记录，筛选 merged_at 非空且 base 为当前默认分支，最多扫描 500 个，选前 3 个。读取单页至多 100 个文件和 100 条 review，并标明潜在截断。
部分项目采用外部合并工具，GitHub PR 的 merged_at 可能不足以代表实际集成；0 个样本不能解释为项目没有合并活动。

Release：按 GitHub API 创建顺序分页，每页 20，最多 100，过滤 draft/prerelease，选前 3 个。该选择不保证 published_at 排序，也不覆盖包注册表、其他分支和所有发布渠道。
标签仅列最近 3 个作为补充，不把标签自动当成正式 Release。对有标签的 Release 解析提交并读取该 SHA 的 Actions；对 PR 读取 head 和 merge SHA 的 Actions。
工作流运行每个 SHA 上限 10 个，可能包含重复或同提交的其他事件。关联只是同 SHA，不证明因果关系；成功的某个运行也不等于所有必需检查通过。

## 时间与复现

每个 API 响应在本地缓存，缓存不进入 Git。source_times 逐端点记录实际缓存写入时间；旧缓存重建时保留该时间，assembled_at 单列资料组装时间。
collected_at 是本档案成功读取来源的最早抓取时间，last_source_fetch_at 为最晚时间。不同端点不是同一事务快照；默认分支文档固定 SHA，PR、Release 与运行状态可能跨越几分钟或更长时间。
公开响应的筛选结果保留于 data，文档保留 blob SHA、行数、信号行号和固定 URL；不镜像整份上游文件或运行日志。它们可能依法或因仓库调整失效，不能承诺永久可访问。

```text
python scripts/collect_research.py --roster research/roster.json --output research/data --cache work/github-cache --workers 6
python scripts/collect_research.py --roster research/roster.json --output research/data --cache work/github-cache --rebuild
python scripts/build_research.py --data research/data --output research
```

默认跳过已有档案；--rebuild 用缓存重建并补充缺少端点，--refresh 才重新请求已缓存来源。读取网络的临时故障允许最多 3 次尝试，403/404 直接记录。这是研究采集的重试策略；当前插件维护任务按项目规则诊断并修复范围内失败。

## 证据分级

1. **书面规定**：人工阅读明确规则，链接到实际文件和行号。
2. **实际观察**：公开提交、PR、review、Release 和工作流状态，保留对应 ID。
3. **候选信号**：脚本在已读文件检测关键词与语法，可能为例子、注释或不适用内容，不能直接认定规则生效。
4. **研究推断**：跨证据解释差异，写明限制与反例。
5. **插件建议**：按任务和项目规模提炼的操作建议，不伪装为公司政策。

summary.json 中特征数字是“至少一个文件命中该候选信号的仓库数”，分母是同类已建档仓库数；不是遵循某规范的比例、质量排名或因果结论。
media 统计包含图标和徽章图片，story 关键词可能只出现在版本号、依赖或历史说明中，playground 可能只是提及；因此不据此断言采用了完整玩法。
未命中只写“所查范围未见”，未知项包括实际分支保护、凭据权限、外部 CI、私有维护决策与历史 Star 数据。

## 内容与使用

比较报告按类别归纳，保留反例。文件与链接检查不替代语义核验；代理指令中的自动发布授权不能从远端仓库推导到用户项目。
第三方仓库内容和数据仍受各自许可证、平台条款及个人信息规则约束；本项目以元数据、定位链接和原创归纳为主，不重分发整仓源码。
展示工具作为补充案例，不占用 60 个核心样本名额。私有仓库不请求公开图表服务，也不把当前私有项目写成公开演示。
