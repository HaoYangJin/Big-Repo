# 开发与验证

运行环境为 Python 3.11+、Git，Python 运行工具只依赖标准库。Node.js 与 Playwright 仅用于开发期浏览器验收。

```sh
python -m unittest discover -s tests
python scripts/build_plugin.py --output ../Big-Repo-dist
python scripts/explore.py --demo --output ../Big-Repo-demo.html
python scripts/explore.py --repo . --output ../Big-Repo-report.html
node tests/explorer.browser.cjs ../Big-Repo-demo.html ../Big-Repo-report.html ../Big-Repo-browser-evidence
```

scripts/runtime_resources.py 是接入与构建共用的运行资源白名单。源仓库 README 中指向不随包分发的资料，会在导出时改为固定版本源码链接。每次修改资源、技能或模板，检查 assets/catalog.json 的能力登记和离线页面能否完整运行。

研究使用 research/ 的唯一源数据；脚本 collect_research.py 与 build_research.py 用于明确发起的采集和报告，不在日常任务中自动联网采集。

维护遵循根目录 AGENTS.md，提交遵循 [提交规范](../skills/git-commit/references/commit-conventions.md)。实际验收范围见 [验证记录](validation.md)。
