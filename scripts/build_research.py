"""Render evidence-located repository profiles and a bounded descriptive comparison."""
from __future__ import annotations

import argparse
from collections import Counter
import html
import json
from pathlib import Path

CATEGORIES = {'sdk': 'API SDK', 'agents': '代理、技能与协议', 'ml': '模型与机器学习',
              'frameworks': '应用与框架', 'infrastructure': '基础设施', 'tools': '语言与开发工具'}
FEATURES = {'tests': '测试命令候选', 'lint': '格式与静态检查候选', 'generated_code': '生成代码提示',
            'release_automation': '自动发布配置候选', 'permissions': '工作流权限声明候选',
            'pinned_actions': '完整 SHA 固定的 Action 引用', 'conventional_commits': '结构化提交约定候选',
            'security': '安全响应入口候选', 'star_history': 'Star History 提及', 'badges': '状态徽章',
            'media': '图片与媒体引用', 'theme_images': '主题图片切换', 'playground': '在线体验提及',
            'community': '社区参与入口候选', 'story': '历史与里程碑提及'}
SHOWCASE = {'增长与活动': ['star_history'], '状态展示': ['badges'], '项目门面': ['media', 'theme_images'],
            '快速体验': ['playground'], '社区参与': ['community'], '项目故事': ['story']}
ADVICE = {
    'sdk': '维护建议：优先核对生成器与手写扩展边界、SDK 版本约束和发布凭据；跨语言 SDK 的流程不能仅按语言复制。',
    'agents': '维护建议：区分可安装技能、示例、协议实现与产品反馈仓库；先确定实际交付物，再选择验证和发布流程。',
    'ml': '维护建议：确认硬件、模型权重、测试矩阵与可用环境；没有运行硬件测试时明确未验证，不能用文档检查替代。',
    'frameworks': '维护建议：确认多包影响、运行时兼容与发布通道；预发布、稳定版和在线演示分别验证。',
    'infrastructure': '维护建议：优先核对组件责任、集成环境和升级兼容；本地单元测试不代表集群或生产部署验证。',
    'tools': '维护建议：区分自举、编译、平台矩阵和插件生态；版本与发布方式依项目规则，不统一强制工具链。',
}


def safe(value):
    return html.escape(str(value or '未知').strip()).replace('|', '\\|').replace('\n', ' ')


def evidence(record, feature):
    return [{'path': d['path'], 'line': line, 'url': d['url'] + f'#L{line}'}
            for d in record.get('documents', []) if d.get('status') == 'inspected'
            for line in d.get('signals', {}).get(feature, [])]


def link(item):
    return f"[{safe(item['path'])}:{item['line']}]({item['url']})"


def doclinks(record, predicate):
    docs = [d for d in record.get('documents', []) if d.get('status') == 'inspected' and predicate(d['path'].lower())]
    return '、'.join(f"[{safe(d['path'])}]({d['url']})" for d in docs[:5]) or '所查范围未取得直接文件证据；其他位置未知'


def profile(record):
    repo = record.get('repository', record['requested_repository'])
    meta = record.get('metadata', {})
    documents = record.get('documents', [])
    inspected = [d for d in documents if d.get('status') == 'inspected']
    text = [f'# {repo}', '', f"类别：{CATEGORIES.get(record['category'], record['category'])}；状态：{record['status']}。",
            '', f"[仓库](https://github.com/{repo}) · [本地证据 JSON](../data/{record['requested_repository'].replace('/', '__')}.json)",
            '', '## 快照与身份', '', f"- 请求名称：{record['requested_repository']}；API 解析名称：{repo}。官方归属按样本维护组织与仓库声明核对，非第三方插件背书。",
            f"- 用途：{safe(meta.get('description'))}",
            f"- 语言：{safe(meta.get('language'))}；许可证：{safe((meta.get('license') or {}).get('spdx_id'))}；归档：{meta.get('archived', '未知')}。",
            f"- Star：{meta.get('stargazers_count', '未知')}；Fork：{meta.get('forks_count', '未知')}；最近 push：{safe(meta.get('pushed_at'))}。这些不是质量或使用人数指标。",
            f"- 默认分支：{safe(meta.get('default_branch'))}；固定提交：`{record.get('default_sha', '未知')}`。",
            f"- 最早证据抓取：{record.get('collected_at', '未知')}；最后抓取：{record.get('last_source_fetch_at', '未知')}；资料组装：{record.get('assembled_at', '未知')}。逐端点时间见 JSON source_times。",
            '', '## 内容、协作与维护', '',
            '| 维度 | 文件证据或采样边界 |', '| --- | --- |',
            '| 文档入口 | ' + doclinks(record, lambda p: 'readme' in p) + ' |',
            '| 贡献与责任归属 | ' + doclinks(record, lambda p: any(s in p for s in ('contribut', 'owners', 'maintain', 'governance'))) + ' |',
            '| AI 指令与技能 | ' + doclinks(record, lambda p: Path(p).name in ('agents.md', 'claude.md', 'skill.md')) + ' |',
            '| 安全响应 | ' + doclinks(record, lambda p: 'security' in p) + ' |',
            '| 包与构建配置 | ' + doclinks(record, lambda p: Path(p).name in ('package.json', 'pyproject.toml', 'cargo.toml', 'go.mod', 'makefile')) + ' |',
            f"| GitHub 工作流 | 目录列出 {len(record.get('workflow_paths', []))} 个，读取 {sum('/workflows/' in d['path'] for d in inspected)} 个；配置存在不等于成功执行 |",
            '', '以下为已读取文件的关键词候选信号，链接定位实际文本；不是逐条规则的语义证明。未命中仅表示采样范围未见，不代表仓库没有该能力。', '',
            '| 维护信号 | 位置 |', '| --- | --- |']
    for feature, title in FEATURES.items():
        if feature in ('star_history', 'badges', 'media', 'theme_images', 'playground', 'community', 'story'):
            continue
        found = evidence(record, feature)
        text.append(f"| {title} | " + ('、'.join(link(e) for e in found[:4]) or '所查文件未命中；实际规则未知') + ' |')
    text += ['', '## 真实变更样本', '', f"默认分支提交样本：{len(record.get('commits', []))}/20；已合并 PR：{len(record.get('pull_requests', []))}/3。",
             'PR 按最近更新的已关闭且已合并到当前默认分支筛选，最多扫描 500 个；不代表最近合并时间排序，也不代表完整审查历史。', '']
    for c in record.get('commits', []):
        text.append(f"- [{c['sha'][:8]}]({c['url']}) {safe(c['subject'])}（{c['date']}）")
    for pr in record.get('pull_requests', []):
        runs = pr.get('merge_commit_workflow_runs', []) + pr.get('head_commit_workflow_runs', [])
        text += ['', f"### [PR #{pr['number']}]({pr['url']}) {safe(pr['title'])}",
                 f"合并：{pr['merged_at']}；merge SHA：`{pr['merge_commit_sha']}`；公开 review 状态：{', '.join(pr.get('review_states', [])) or '采样未取得'}。",
                 f"变更文件：{len(pr.get('files', []))} 个（单页上限 100，可能截断：{pr.get('files_may_be_truncated')}）。",
                 '涉及路径：' + '、'.join('`' + safe(p) + '`' for p in pr.get('files', [])[:12]) + '。']
        for run in {r['id']: r for r in runs}.values():
            text.append(f"- [运行 {run['id']}]({run.get('html_url')}) {safe(run.get('name'))}；事件 {safe(run.get('event'))}；状态 {safe(run.get('status'))}/{safe(run.get('conclusion'))}；工作流 `{safe(run.get('path'))}`。")
        if not runs:
            text.append('未取得该 head/merge SHA 的 GitHub Actions 运行；外部 CI、删除或过期记录均未知。')
    text += ['', '## 版本与发布', '', f"正式 GitHub Release 样本：{len(record.get('releases', []))}/3。从最多 100 个 API 创建顺序记录中过滤 draft/prerelease；不等于所有分支或包的最近发布时间排序。", '']
    for release in record.get('releases', []):
        text += [f"- [{safe(release['tag'])}]({release['url']})：{release['published_at']}；提交 `{release.get('commit_sha') or '未知'}`；资产 {len(release.get('assets', []))} 个。"]
        for run in release.get('workflow_runs', []):
            text.append(f"  - [关联运行 {run['id']}]({run.get('html_url')})：{safe(run.get('name'))}，{safe(run.get('event'))}，{safe(run.get('conclusion'))}。同 SHA 关联不证明由该 Release 触发。")
    text += ['最近标签：' + ('、'.join('`' + safe(t['name']) + '`' for t in record.get('tags', [])) or '未取得') + '。',
             'GitHub Release 不足时不推断未发布：包注册表、外部发布与标签式发布均需单独核对。', '', '## 仓库展示与玩法', '',
             '| 固定类别 | 观察位置 |', '| --- | --- |']
    for title, features in SHOWCASE.items():
        found = [e for f in features for e in evidence(record, f)]
        text.append(f"| {title} | " + ('、'.join(link(e) for e in found[:4]) or '采样未见直接信号；未强行补齐') + ' |')
    text += ['', '## 解释、建议与限制', '', ADVICE.get(record['category'], ''),
             '本段是插件建议，不是该仓库明文要求。现有工作流、审查规则和展示内容应以链接原文及目标任务为准。',
             '未知项包括有效分支保护、令牌实际权限、外部 CI、私有维护决策、历史 Star 数据；未访问不等于不存在。',
             f'读取成功 {len(inspected)} 个文档/配置；工作流按名称优先采样至多 12 个，技能/插件目录各至多 3 个代表入口，大于 400 KB 文件跳过。',
             '', '## 采集缺口', '']
    text.extend('- ' + safe(e) for e in record.get('errors', []))
    if not record.get('errors'):
        text.append('没有接口错误记录；这不表示没有上述采样限制。')
    text += ['', '## 文件来源清单', '']
    for d in documents:
        text.append(f"- [{safe(d['path'])}]({d['url']})：{d.get('lines', 0)} 行，blob `{d['sha']}`。" if d.get('status') == 'inspected' else f"- `{d['path']}`：{d['status']}。")
    return '\n'.join(text) + '\n'


def comparison(records, summary):
    def cite(repo, path, line):
        record = next((r for r in records if r['requested_repository'] == repo), {})
        doc = next((d for d in record.get('documents', []) if d.get('path') == path and d.get('status') == 'inspected'), None)
        return f"[{repo}/{path}:{line}]({doc['url']}#L{line})" if doc else f'{repo}（该样本来源未取得）'

    coverage = summary['coverage']
    text = ['# 官方仓库的共性、差异与 AI 维护建议', '',
            '## 结论与证据级别', '',
            '可复用的不是某一家公司统一的文件清单，而是：先找到项目真实规则与生成源，明确责任和验证证据，再按项目发布渠道交付。展示功能应帮助理解项目，并承担与其价值相称的维护成本。',
            '这是一项有边界的案例研究。档案深入到配置、真实变更与发布关联，但未穷尽源码、平台权限、外部 CI 或全部历史；候选信号统计与下文人工核对的案例分开解释。',
            '', '## 采集覆盖', '',
            f"固定样本 {summary['records']} 个，读取文档/配置/代表入口 {coverage['documents']} 个，默认分支提交 {coverage['commits']} 条，已合并 PR {coverage['pull_requests']} 个，正式 GitHub Release {coverage['releases']} 个。",
            f"关联 Actions 运行记录 {coverage['workflow_runs']} 条（未按 run ID 全局去重），接口错误 {coverage['errors']} 条。实际状态、时间和限制以各档案为准。", '',
            '[全部分类档案](README.md) · [方法与限制](METHODOLOGY.md) · [机器可读统计](summary.json) · [来源索引](source-index.json)', '',
            '## 按内容类型比较', '',
            '| 类型 | 主要维护对象与差异 | AI 托管的关键适配 |', '| --- | --- | --- |',
            '| SDK | 生成源、手写扩展、语言运行时及包注册表；同一组织的不同语言 SDK 也可能采用不同生成器 | 先核对可编辑边界与生成流程，再选择兼容性测试和版本更新 |',
            '| 代理、技能与协议 | 技能内容库、产品反馈仓库、协议实现与多包 SDK 交付物不同 | 先确认真正可修改的源码或内容，以及安装与平台行为的验证方式 |',
            '| 模型与机器学习 | 构建、硬件、权重、可选依赖和测试矩阵带来环境差异 | 明确硬件与网络依赖，未运行的设备测试单列，不能以本地通过替代 |',
            '| 应用与框架 | 多包、运行时、预发布与多条稳定维护线并存 | 固定受影响包、分支和通道，不只找一个“最新版本” |',
            '| 基础设施 | 组件责任、兼容性、集群集成和多版本维护较重要 | 识别责任人和环境，变更验证与生产部署严格分开 |',
            '| 语言与开发工具 | 自举、平台矩阵、镜像及非 GitHub 贡献渠道 | 先检查贡献入口和 AI 使用政策，不能默认所有项目都接受 AI 创建的 PR |', '',
            '上表是跨案例解释和插件建议；不声称每个类别的所有仓库都采用同一种实现。', '',
            '## 已核对案例：共性与不能统一的地方', '',
            '### 生成代码要找源头，但“生成文件一律不能改”过于粗糙', '',
            'OpenAI Python 的代理说明明确区分生成 SDK 与手写政策、测试和示例。Anthropic Python 进一步说明某些文件混合生成内容与手写内容，需要定位具体行的来源。OpenAI .NET 的贡献指南则描述 TypeSpec、Generated 与 Custom 目录。共性是定位来源，区别是定位和再生成机制。',
            cite('openai/openai-python', 'AGENTS.md', 3) + '；' + cite('anthropics/anthropic-sdk-python', 'CLAUDE.md', 9) + '；' + cite('openai/openai-dotnet', 'CONTRIBUTING.md', 9) + '。', '',
            '### 提交、版本与发布是关联流程，不是一套通用命令', '',
            'Anthropic Python 的说明将结构化提交与 release-please 联系起来；MCP Python 的发布文档说明版本来自标签、发布工作流取自被标记提交，且存在不同发布线。Svelte 的贡献说明强调真实测试命令和 UI 改动的截图或视频。',
            cite('anthropics/anthropic-sdk-python', 'CLAUDE.md', 354) + '；' + cite('modelcontextprotocol/python-sdk', 'RELEASE.md', 17) + '；' + cite('sveltejs/svelte', 'CONTRIBUTING.md', 85) + '。',
            '插件因此记录验证命令、目标提交、受影响组件和发布通道，不把 Conventional Commits、某个发布工具或某个测试命令当成所有项目的强制规则。', '',
            '### 责任和权限要有实际边界', '',
            'Kubernetes 的 OWNERS 列出不同文件的 reviewers 与 approvers。OpenAI Python 的说明限制发布凭据与 OIDC 权限的使用范围。文件内容能证明项目声明了规则，不能单独证明平台设置已生效。',
            cite('kubernetes/kubernetes', 'OWNERS', 5) + '；' + cite('openai/openai-python', 'AGENTS.md', 39) + '。', '',
            '### 仓库身份和贡献渠道不能省略', '',
            'Go README 明确说明 GitHub 镜像身份，贡献指南转向项目贡献文档。VS Code README 区分 Code - OSS 仓库和产品发行版。Rust 的代理说明要求遵守项目 LLM 使用政策。它们说明：维护对象、产品名称和可接受贡献方式都需要单独核对。',
            cite('golang/go', 'README.md', 10) + '；' + cite('golang/go', 'CONTRIBUTING.md', 29) + '；' + cite('microsoft/vscode', 'README.md', 5) + '；' + cite('rust-lang/rust', 'AGENTS.md', 3) + '。', '',
            'AI 使用规则本身也存在差异：Neovim 的代理说明要求 AI-assisted 提交尾注，而 Rust 的说明包含更细的允许与禁止范围。插件必须读取目标项目的实际政策，不能把一种披露方式或限制推广到全部项目。',
            cite('neovim/neovim', 'AGENTS.md', 3) + '；' + cite('rust-lang/rust', 'AGENTS.md', 10) + '。', '',
            'Helm 的代理说明明确区分 v3/dev-v3 与 v4/main；这与档案中同时出现多条稳定发布线一致。发布准备必须绑定组件和维护分支，而不是只修改一个最大版本号。',
            cite('helm/helm', 'AGENTS.md', 10) + '。', '',
            '### 技能仓库也有独立的打包与授权边界', '',
            'Anthropic Skills 说明每个技能的独立目录、示例用途以及不同资源的许可证范围，不能把“公开可读”当作全部资源采用相同许可。插件据此保留资源归属、相对引用和运行环境，格式通过后仍单列平台加载验证。',
            cite('anthropics/skills', 'README.md', 14) + '。', '',
            '## 固定维度：仓库展示与玩法', '',
            '固定检查增长活动、状态徽章、项目门面、快速体验、社区参与和项目故事。采用情况与推荐价值分别记录；某个大型项目没有某项内容，不构成应当补齐的缺陷。',
            f"本次所查文件中 Star History 候选信号命中 {summary['features']['star_history']}/{summary['records']} 个仓库；这不代表未查目录或历史版本也未使用。Star History 作为补充工具案例提供，不写成官方仓库的共同要求。",
            '图片统计包含徽章，主题图片信号可能来自更新记录中的 HTML 说明，在线体验信号可能来自 bug 模板；不能把这些数字解释为完整功能采用率。',
            '[六类玩法、依赖与移除方式](../plugins/repo-maintainer/skills/repo-showcase/references/showcase-catalog.md) · [可复用草稿](../plugins/repo-maintainer/templates/showcase.md)', '',
            '## 候选信号分布', '',
            '分子为至少一个已读文件命中关键词的仓库数，分母为该类档案数；这是发现线索，不是质量分数或规范遵循率。', '',
            '| 类别 | 测试候选 | 生成代码提示 | 自动发布候选 | 徽章 | 主题图片候选 | 在线体验提及 |', '| --- | --- | --- | --- | --- | --- | --- |']
    for category, label in CATEGORIES.items():
        stats = summary['categories'][category]
        text.append('| ' + label + ' | ' + ' | '.join(f"{stats['features'][f]}/{stats['n']}" for f in ('tests', 'generated_code', 'release_automation', 'badges', 'theme_images', 'playground')) + ' |')
    text += ['', '## 转化为插件的决策', '',
             '- 用任务记录绑定目标、范围、基准、操作和验证；项目现有规则优先。',
             '- 将首次非预期失败交接设为本插件默认，不宣称它是 60 个仓库共同采用的策略。',
             '- 本地验证、远端 CI、PR 创建和正式发布分别报告；生成发布草稿不执行发布。',
             '- 展示内容先预览，再在授权范围内应用；私有仓库不接入公开统计服务。',
             '- 小型仓库保留最小有效流程，不强制复制大型组织的全部门禁。', '',
             '## 身份迁移与缺口', '']
    for r in records:
        if r.get('repository') != r['requested_repository']:
            text.append(f"- {r['requested_repository']} → {r.get('repository', '未取得')}，保留原样本标识与解析后的来源。")
        if len(r.get('pull_requests', [])) < 3 or len(r.get('releases', [])) < 3 or r.get('errors'):
            text.append(f"- [{r['requested_repository']}](profiles/{r['requested_repository'].replace('/', '__')}.md)：PR {len(r.get('pull_requests', []))}/3，正式 GitHub Release {len(r.get('releases', []))}/3，接口错误 {len(r.get('errors', []))}。不足仅表示本方法取得的实际样本。")
    return '\n'.join(text) + '\n'


def build(data_dir, output):
    output = Path(output)
    (output / 'profiles').mkdir(parents=True, exist_ok=True)
    records = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(Path(data_dir).glob('*.json'))]
    summary = {'records': len(records), 'categories': {}, 'features': {}, 'coverage': {}}
    sources = []
    index = ['# 官方仓库分类档案', '', '[研究方法](METHODOLOGY.md) · [比较报告](COMPARISON.md) · [来源索引](source-index.json)', '',
             f'本次共 {len(records)} 个档案。数字仅描述指定样本和检查范围；细节与未知项见各档案。', '']
    for category, label in CATEGORIES.items():
        group = [r for r in records if r['category'] == category]
        summary['categories'][category] = {'n': len(group), 'features': {f: sum(bool(evidence(r, f)) for r in group) for f in FEATURES}}
        index += ['## ' + label, '', '| 仓库 | 文档读取 | PR | 正式 Release | 状态 |', '| --- | --- | --- | --- | --- |']
        for r in group:
            name = r['requested_repository'].replace('/', '__')
            (output / 'profiles' / (name + '.md')).write_text(profile(r), encoding='utf-8', newline='\n')
            index.append(f"| [{r.get('repository', r['requested_repository'])}](profiles/{name}.md) | {sum(d.get('status') == 'inspected' for d in r.get('documents', []))} | {len(r.get('pull_requests', []))} | {len(r.get('releases', []))} | {r['status']} |")
            sources.append({'repository': r.get('repository', r['requested_repository']),
                            'record': 'data/' + name + '.json', 'default_sha': r.get('default_sha'),
                            'collected_at': r.get('collected_at'), 'last_source_fetch_at': r.get('last_source_fetch_at'),
                            'documents': [{k: d.get(k) for k in ('path', 'sha', 'url', 'status')} for d in r.get('documents', [])]})
        index.append('')
    for f in FEATURES:
        summary['features'][f] = sum(bool(evidence(r, f)) for r in records)
    summary['coverage'] = {'documents': sum(sum(d.get('status') == 'inspected' for d in r.get('documents', [])) for r in records),
                           'commits': sum(len(r.get('commits', [])) for r in records),
                           'pull_requests': sum(len(r.get('pull_requests', [])) for r in records),
                           'releases': sum(len(r.get('releases', [])) for r in records),
                           'errors': sum(len(r.get('errors', [])) for r in records),
                           'workflow_runs': sum(len(p.get('merge_commit_workflow_runs', [])) + len(p.get('head_commit_workflow_runs', [])) for r in records for p in r.get('pull_requests', [])) + sum(len(p.get('workflow_runs', [])) for r in records for p in r.get('releases', []))}
    (output / 'README.md').write_text('\n'.join(index), encoding='utf-8', newline='\n')
    (output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / 'source-index.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / 'COMPARISON.md').write_text(comparison(records, summary), encoding='utf-8', newline='\n')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.data, args.output), ensure_ascii=False, indent=2))
