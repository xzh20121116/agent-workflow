<p align="center">
    <a href="https://github.com/xzh20121116/agent-workflow/stargazers" alt="Stars">
        <img src="https://img.shields.io/github/stars/xzh20121116/agent-workflow?style=flat-square&logo=github" /></a>
    <a href="https://github.com/xzh20121116/agent-workflow/blob/master/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/xzh20121116/agent-workflow?style=flat-square" /></a>
    <a href="https://github.com/xzh20121116/agent-workflow/issues" alt="Issues">
        <img src="https://img.shields.io/github/issues/xzh20121116/agent-workflow?style=flat-square" /></a>
    <a href="https://github.com/xzh20121116/agent-workflow/releases/latest" alt="Latest Release">
        <img src="https://img.shields.io/github/v/release/xzh20121116/agent-workflow?style=flat-square" /></a>
</p>

<p align="center">
    <strong>Agent Workflow</strong><br/>
    AI 编程代理的编排器-子代理工作流技能。<br/>
    让你的 AI 代理变成纪律严明的项目经理，将工作委派给专门的子代理。
</p>

<p align="center">
    <a href="README.md"><strong>English</strong></a>
    ·
    <a href="README_zh-CN.md"><strong>中文</strong></a>
</p>

---

## 为什么需要 Agent Workflow

AI 代理面对复杂任务时，常常会：

- 事事亲力亲为，不会委派
- 需求澄清后就停下来，不会继续推进
- 生成丑陋、通用的 UI，充满明显的 AI 味
- 跳过验证就声称完成

Agent Workflow 通过将主线程变成**编排器（Orchestrator）**来解决这些问题。编排器只做三件事：与用户对话、管理状态、委派工作给专门的子代理。它永远不直接碰代码。

## 核心架构

```
用户 ←→ 编排器（主线程）
              │
              ├── 实现子代理
              ├── 规格合规审查
              ├── 代码质量审查
              ├── UI 审查（前端任务）
              ├── 验证子代理
              └── QA 子代理
```

编排器只有**四项职责**：

1. **与用户对话** — 需求澄清、确认、最终交付
2. **管理状态** — 读写 state.json、需求文档、验收标准、计划
3. **委派子代理** — 构建自包含的 SubagentContextPacket，通过 Agent 工具分发
4. **综合结果** — 处理实现者状态，决定下一步行动

编排器**永远不**直接读源码、跑测试、写实现代码或做审查。

## 核心特性

| 特性 | 说明 |
|------|------|
| **编排器-子代理分离** | 主线程协调，子代理执行，杜绝自行编码 |
| **SubagentContextPacket** | 自包含提示词：任务、目标、文件、非目标、验证条件，不泄漏对话历史 |
| **两阶段审查** | 规格合规（做对了吗？）+ 代码质量（做好了吗？） |
| **UI 审查** | 捕获 AI 生成的 UI 问题：丑字体、霓虹渐变、通用布局。AI Slop Score 0-10 分 |
| **前端设计约束** | 在实现提示词中注入排版、配色、布局、动效规则 |
| **实现者四状态返回** | DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED，编排器逐个处理 |
| **检查点 & 恢复** | 通过 handoff.md 在上下文重置后恢复进度，永远不从记忆恢复 |
| **漂移检测** | 每个阶段后验证工作是否仍服务于原始意图 |

## 阶段流程

```
requirement_clarification  （编排器与用户对话）
→ requirements             （编排器写 requirements.md）
→ acceptance               （编排器写 acceptance.md，用户确认）
→ plan                     （编排器写 plan.md）
→ implementation           （子代理实现，高风险用 worktree 隔离）
→ spec_compliance_review   （子代理：做对了吗？）
→ code_quality_review      （子代理：做好了吗？）
→ ui_review                （子代理：仅前端任务，抓 AI 味）
→ verification             （子代理：跑测试、lint、构建）
→ qa                       （子代理：验证验收标准）
→ final_handoff            （编排器向用户汇报）
```

## 安装

### Claude Code

```bash
# 克隆到 skills 目录
git clone https://github.com/xzh20121116/agent-workflow.git ~/.claude/skills/agent-workflow

# 或者从统一位置创建符号链接
git clone https://github.com/xzh20121116/agent-workflow.git ~/.agent-workflow
ln -s ~/.agent-workflow/skills/agent-workflow-init ~/.claude/skills/agent-workflow-init
ln -s ~/.agent-workflow/skills/agent-workflow-start ~/.claude/skills/agent-workflow-start
```

### Codex App

```bash
# 克隆到 skills 目录
git clone https://github.com/xzh20121116/agent-workflow.git ~/.codex/skills/agent-workflow

# 或者符号链接
git clone https://github.com/xzh20121116/agent-workflow.git ~/.agent-workflow
ln -s ~/.agent-workflow/skills/agent-workflow-init ~/.codex/skills/agent-workflow-init
ln -s ~/.agent-workflow/skills/agent-workflow-start ~/.codex/skills/agent-workflow-start
```

### 通用（任意宿主）

```bash
git clone https://github.com/xzh20121116/agent-workflow.git ~/.agent-workflow

# 然后将 skills 符号链接或复制到你的宿主 skills 目录
# Claude Code: ~/.claude/skills/
# Codex: ~/.codex/skills/
# 其他: 查看你宿主的 skill 发现路径
```

## 使用

### 1. 初始化项目

```
/agent-workflow-init
```

或显式调用：

```bash
python skills/agent-workflow-init/scripts/init_agent_workflow.py --project-root .
```

### 2. 发起需求

```
用重任务流程处理：用户个人中心增加修改手机号功能
```

或显式调用：

```bash
python skills/agent-workflow-start/scripts/start_agent_workflow.py --project-root . --title "修改手机号功能" --risk-level medium
```

### 3. 前端任务（带设计约束）

```
用重任务流程美化 src/pages/profile/index.tsx 页面
```

前端任务会自动：
- 使用 `frontend-implementer-prompt.md`（包含设计约束）
- 在代码质量审查后增加 UI 审查阶段
- 检查 AI 味道（Inter 字体、霓虹渐变、三等分列等）

## 子代理提示词模板

每个角色都有专用的提示词模板，位于 `skills/agent-workflow-start/references/`：

| 模板 | 角色 | 核心特点 |
|------|------|----------|
| `implementer-prompt.md` | 后端实现 | SubagentContextPacket、四状态返回 |
| `frontend-implementer-prompt.md` | 前端实现 | 设计约束（排版、配色、布局、动效） |
| `spec-reviewer-prompt.md` | 规格合规审查 | "不要相信报告"指令 |
| `code-quality-reviewer-prompt.md` | 代码质量审查 | 结构、正确性、可维护性 |
| `ui-reviewer-prompt.md` | UI/视觉审查 | AI 味检测、响应式检查、无障碍 |
| `verification-prompt.md` | 测试/lint/构建 | 运行项目测试套件 |
| `qa-prompt.md` | 验收标准 | 逐条验证验收条件 |

## 设计约束（前端）

`frontend-implementer-prompt.md` 注入以下规则，防止丑陋的 AI 生成 UI：

| 类别 | 规则 |
|------|------|
| **排版** | 禁用 Inter/Roboto/Arial，推荐 Geist/Outfit/Satoshi，文字颜色禁用 #000000 |
| **配色** | 最多 1 个强调色，饱和度 < 80%，禁用霓虹/紫色渐变 |
| **布局** | 禁用三等分列，宽松留白（py-24+），非对称网格 |
| **组件** | 大元素禁用 rounded-full，禁用重阴影 |
| **动效** | 自定义 cubic-bezier，尊重 prefers-reduced-motion |
| **内容** | 禁用占位符名字、禁用 em-dash，只用真实文案 |

## 风险等级与子代理策略

| 风险等级 | 实现 | 审查 | 验证 | 隔离方式 |
|----------|------|------|------|----------|
| `critical` | 必须 | 规格 + 质量 + UI | 必须 | worktree |
| `high` | 必须 | 规格 + 质量 + UI | 必须 | worktree |
| `medium` | 必须 | 按需 | 必须 | 共享 |

## 项目结构

```
.
├── skills/
│   ├── agent-workflow-init/          # 项目级初始化器
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   └── agent-workflow-guide.md
│   │   ├── assets/templates/
│   │   │   ├── AGENTS.md.template
│   │   │   └── change-request-template.md
│   │   └── scripts/
│   │       ├── init_agent_workflow.py
│   │       └── install_symlinks.sh
│   └── agent-workflow-start/         # 需求级入口
│       ├── SKILL.md
│       ├── references/
│       │   ├── start-guide.md
│       │   ├── implementer-prompt.md
│       │   ├── frontend-implementer-prompt.md
│       │   ├── spec-reviewer-prompt.md
│       │   ├── code-quality-reviewer-prompt.md
│       │   ├── ui-reviewer-prompt.md
│       │   ├── verification-prompt.md
│       │   └── qa-prompt.md
│       └── scripts/
│           └── start_agent_workflow.py
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── LICENSE
└── README.md
```

## 致谢

- [Aegis](https://github.com/GanyuanRan/Aegis) — 面向 AI 编程代理的 baseline-first、evidence-driven 工作流方法包
- [Superpowers](https://github.com/obra/superpowers) — Jesse Vincent 创建的可组合代理技能

## 许可证

MIT License。见 [LICENSE](LICENSE)。
