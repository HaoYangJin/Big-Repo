<!-- big-repo:workflow:start -->
## 开发任务与反馈的自动交付

本项目已显式启用 Big-Repo 客户端入口。收到开发需求、缺陷或测试/CI 反馈时，读取 `.big-repo/config.json` 和 `./skills/maintenance-delivery/SKILL.md`。本项目策略：验证、独立审查及全部 CI 通过后，锁定最终 SHA 自动合并。普通问答、规划和只读审查不创建任务、不提交或执行远端写入；用户本轮更窄限制优先。

由当前 AI 客户端执行：理解任务及项目规则 → 运行 `python ./scripts/project_workflow.py begin --repo . --objective "实际需求" --allowed-path "实际改动范围"`（已有任务先 status）→ 开发并同步本轮相关说明（展示仅按已选择的策略同步）→ 精确提交 → check → 独立 AI 审查并用 review 登记真实结论 → deliver。严格遵守配置的交付终点，等待中的 CI 只读等待；结果不确定先查询，不盲目重试写入。

命令详情与故障恢复见 `./references/project-workflow.md`。这是依赖客户端遵循协议的协作流程，不能拦截绕过脚本的 Git 操作。保留用户工作及 Git 元数据内的任务/日志；不伪造验证或独立审查。配置不取代用户授权、项目规则与客户端权限；不读取凭据值，不设置定时任务。版本发布只有获明确版本授权才执行。
<!-- big-repo:workflow:end -->
