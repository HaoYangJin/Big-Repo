<!-- big-repo:workflow:start -->
## 开发任务与反馈的自动交付

本项目已接入 big-repo。收到开发需求、缺陷反馈或本轮测试/CI/审查反馈时，读取 `.big-repo/config.json` 和 `./skills/maintenance-delivery/SKILL.md`，复用项目配置完成本轮维护和交付，用户无需再说“提交、上传、创建 PR”。普通问答、只读审查和用户明确的更窄限制按其原范围执行。

由当前 AI 客户端执行：理解任务及项目规则 → 运行 `python ./scripts/project_workflow.py begin --repo . --objective "实际需求" --allowed-path "实际改动范围"`（已有任务先 status）→ 开发并同步相关说明与托管展示（repo_tools.py showcase-sync，核实公开性后才加 --public）→ 按项目约定精确提交 → check → 独立 AI 审查并用 review 登记真实结论 → deliver。begin 会复用事件/任务记录，deliver 会核对远端状态，等待 CI 或处理失败后继续同一任务，不能把推送或创建 PR 当作已合并。

命令详情与故障恢复见 `./references/project-workflow.md`。保留用户已有工作；任务/日志保存在 Git 元数据内，不提交、不伪造验证或独立审查。配置不取代用户授权、项目规则与客户端权限；不读取或保存凭据值，不设置定时任务。版本发布遵循 explicit-request 策略，只有用户明确指定版本才执行。
<!-- big-repo:workflow:end -->
