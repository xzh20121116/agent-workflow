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

## 与 Aegis、Superpowers 的对比

Agent Workflow 的灵感来自 [Aegis](https://github.com/GanyuanRan/Aegis) 和 [Superpowers](https://github.com/obra/superpowers)，但走了一条不同的路。以下是三者的详细对比：

### 架构

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **核心模型** | 编排器-子代理，严格分离 | baseline-first 方法包，按风险路由 | 可组合的自动触发技能 |
| **主线程角色** | 纯协调者，永远不碰代码 | 协调者 + baseline 读取阶段 | 技能按任务自动触发 |
| **子代理分发** | SubagentContextPacket（自包含） | 子代理驱动 + baseline 上下文 | 子代理驱动，计划清晰到"初级工程师能执行" |
| **风险路由** | 3 级（critical/high/medium），逐级升级隔离 | 低/中/高复杂度路由 | 所有任务统一流程 |
| **TDD 强制** | 可选（项目自行决定） | 风险自适应（严格/轻量/跳过） | 严格的 RED-GREEN-REFACTOR |

### 审查与验证

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **审查阶段** | 规格合规 → 代码质量 → UI 审查 | baseline + 两阶段审查 | 两阶段代码审查 |
| **UI/前端审查** | 专用 UI 审查，AI Slop Score 0-10 分 | 不包含 | 不包含 |
| **设计约束** | 内置前端设计规则（排版、配色、布局、动效） | 不包含 | 不包含 |
| **完成门禁** | 证据包 + QA 验证 | 证据门禁 + 残余风险追踪 | Evidence over claims |
| **实现者状态** | 四状态返回（DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED） | 子代理驱动 | 计划驱动 |

### 前端能力

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **前端任务检测** | 自动检测 .tsx/.vue/.html 和 UI 相关关键词 | 不包含 | 不包含 |
| **AI 味检测** | 专用 UI 审查检查 Inter 字体、霓虹渐变、三等分列、占位符内容 | 不包含 | 不包含 |
| **设计系统注入** | 排版、配色、布局、动效、图标约束写入实现者提示词 | 不包含 | 不包含 |
| **响应式检查** | 375px 手机、768px 平板、44px 触控目标 | 不包含 | 不包含 |

### 安装与多宿主

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **安装复杂度** | `git clone` + 符号链接，零配置 | 引导式提示词 + `aegis-doctor.py` 验证 | 逐宿主插件安装 |
| **配置面** | 极简（每个请求指定风险等级） | 丰富（activation mode、TDD mode、host registry） | 极简 |
| **支持宿主** | Claude Code、Codex App（通用 via SKILL.md） | 15+ 宿主（多数待验证） | 7 宿主 |
| **验证工具** | 手动（在项目中跑测试） | `aegis-doctor.py` + JSON 健康检查 | 手动 |

### Agent Workflow 的优势

**前端项目。** Agent Workflow 是三者中唯一内置前端设计约束和 UI 审查阶段的。如果你的 AI 代理生成的 UI 用着 Inter 字体、霓虹渐变和三等分布局，Agent Workflow 能在上线前抓住它。

**编排器纪律。** 严格的"编排器永远不碰代码"规则解决了常见的主线程自己编码而非委派的问题。Aegis 和 Superpowers 更信任代理；Agent Workflow 更信任流程。

**更简单的心智模型。** 两个 skill（`init` + `start`），最小配置，不需要 doctor 脚本。克隆、符号链接、开始用。

**实现者状态清晰。** 四状态返回（DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED）给编排器明确的决策点，而不是假设成功。

### 其他工具的优势

**Aegis 更适合：**
- 复杂的企业级代码库，改动前需要 baseline 读取
- 需要风险自适应 TDD 的团队（高风险严格，低风险轻量）
- 多宿主环境，10+ 种不同的 AI 编程代理
- Bug 修复需要双轨闭环（修复轨 + 退役轨）

**Superpowers 更适合：**
- 把 TDD 强制作为不可妥协纪律的团队
- 统一流程（不按风险路由）是优势而非限制的项目
- 使用多种宿主平台的环境（7 种宿主）

### 选择指南

| 场景 | 推荐 |
|------|------|
| 前端 + 后端项目，关注 UI 质量 | **Agent Workflow** |
| 复杂遗留代码库，改动前需要 baseline | **Aegis** |
| TDD 优先团队，要严格的红-绿-重构 | **Superpowers** |
| 快速实现功能，最小安装开销 | **Agent Workflow** |
| 多宿主团队（10+ 种不同 AI 代理） | **Aegis** |
| 需要证据门禁完成 + 风险追踪 | **Aegis** |
| 需要防止 AI 生成丑陋 UI | **Agent Workflow** |
| 简单可组合技能，无工作流开销 | **Superpowers** |

## 致谢

- [Aegis](https://github.com/GanyuanRan/Aegis) — 面向 AI 编程代理的 baseline-first、evidence-driven 工作流方法包
- [Superpowers](https://github.com/obra/superpowers) — Jesse Vincent 创建的可组合代理技能

## 许可证

MIT License。见 [LICENSE](LICENSE)。
