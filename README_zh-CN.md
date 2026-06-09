# Agent Workflow

[English](README.md) | 中文

AI 编程代理的编排器-子代理工作流技能。让你的 AI 代理变成一个纪律严明的项目经理，将工作委派给专门的子代理，而不是事事亲力亲为。

## 这是什么

主线程变成一个**编排器（Orchestrator）**，只做四件事：

1. 与你对话（需求澄清、确认）
2. 管理状态（写需求文档、验收标准、计划）
3. 委派子代理（实现、审查、验证、QA）
4. 汇报结果

编排器**永远不会**直接碰代码。所有编码任务都交给独立的子代理完成。

## 核心特性

- **编排器-子代理分离** — 主线程协调，子代理执行
- **SubagentContextPacket** — 自包含的提示词，不泄漏对话历史
- **两阶段审查** — 规格合规（做对了吗？）+ 代码质量（做好了吗？）
- **UI 审查** — 捕获 AI 生成的 UI 问题（丑字体、霓虹渐变、通用布局）
- **前端设计约束** — 在实现提示词中注入设计规则
- **检查点 & 恢复** — 上下文重置后不丢失进度，永远不从记忆恢复
- **实现者四状态返回** — DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED

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
├── LICENSE
└── README.md
```

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

- **排版**：禁用 Inter/Roboto/Arial，推荐 Geist/Outfit/Satoshi
- **配色**：最多 1 个强调色，饱和度 < 80%，禁用霓虹/紫色渐变
- **布局**：禁用三等分列，宽松留白（py-24+），非对称网格
- **组件**：大元素禁用 rounded-full，禁用重阴影
- **动效**：自定义 cubic-bezier，尊重 prefers-reduced-motion
- **内容**：禁用占位符名字、禁用 em-dash，只用真实文案

## 致谢

- [Aegis](https://github.com/GanyuanRan/Aegis) — AI 编程代理方法包
- [Superpowers](https://github.com/obra/superpowers) — 可组合的代理技能

## 许可证

MIT
