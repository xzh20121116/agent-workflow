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

<h1 align="center">Agent Workflow</h1>

<p align="center"><strong>别再让 AI 一边聊天一边乱改你的代码库。</strong></p>

<p align="center">
    给 Claude Code、Codex 等 AI 编程代理使用的轻量工作流技能包。<br/>
    把"自由发挥的程序员"变成"会澄清需求、会分工、会审查、会验证、会交付证据的项目经理型 Agent"。
</p>

<p align="center">
    <a href="README.md"><strong>English</strong></a>
    ·
    <a href="README_zh-CN.md"><strong>中文</strong></a>
</p>

---

## 为什么需要它

AI 编程代理很强。但给它一个复杂任务，你会看到：

- 需求没澄清就开工，代码写了一半才发现理解错了
- 主线程又聊天又写代码又跑测试，上下文越来越长，压缩几次之后目标漂移了
- 做到后面忘记最初要什么，开始自己发挥
- 跑都没跑就说"已完成"，你一问"测了吗？"它说"理论上应该可以"
- 你追问一个细节，它把之前做的全推翻重来

**Agent Workflow 通过一条规则解决这些问题：主线程永远不碰代码。**

## Before / After

### 没有 Agent Workflow

```
用户:  给个人中心加手机号修改功能
AI:    好的，我来改几个文件
AI:    [改了 6 个文件]
AI:    已完成
用户:  测了吗？
AI:    理论上应该可以
用户:  旧手机号要验证吗？
AI:    好的，我加上
AI:    [又改了 4 个文件]
AI:    已完成
用户:  上下文越来越长了...
AI:    [上下文已压缩，忘记了之前的讨论]
```

### 有 Agent Workflow

```
用户:  用重任务流程处理：个人中心增加修改手机号功能

马斯克:
  1. "需要哪些验证方式？" → 短信验证码
  2. "旧手机号需要验证吗？" → 需要
  3. 写 requirements.md → 用户确认
  4. 写 acceptance.md → 用户确认
  5. 写 plan.md

  ── 派发【实现子代理】──
     返回: DONE (4 files, tests passing)

  ── 派发【规格合规审查】──
     结果: PASS — 需求全部覆盖

  ── 派发【代码质量审查】──
     结果: PASS

  ── 派发【验证子代理】──
     结果: PASS — 12 tests, 0 failures

  ── 派发【QA 子代理】──
     结果: PASS — 8/8 验收标准

  → 交付：功能完成，附带测试证据
```

用户回答了 3 个问题。马斯克管理了剩下的一切。每一步都有证据。

## 工作原理

```mermaid
graph LR
    User["用户"] <-->|"澄清、确认、交付"| O["马斯克<br/>(主线程)"]
    O -->|"写"| R["requirements.md"]
    O -->|"写"| A["acceptance.md"]
    O -->|"写"| P["plan.md"]

    O -->|"委派"| IMP["实现子代理"]
    O -->|"委派"| SR["规格合规审查"]
    O -->|"委派"| QR["代码质量审查"]
    O -->|"委派"| UI["UI 审查<br/>(仅前端)"]
    O -->|"委派"| VER["验证子代理"]
    O -->|"委派"| QA["QA 子代理"]

    IMP -->|"状态 + 证据"| O
    SR -->|"通过/不通过"| O
    QR -->|"通过/不通过"| O
    UI -->|"AI Slop Score"| O
    VER -->|"测试结果"| O
    QA -->|"验收检查"| O

    style O fill:#2563EB,stroke:#1D4ED8,color:#fff
    style IMP fill:#10B981,stroke:#059669,color:#fff
    style SR fill:#F59E0B,stroke:#D97706,color:#fff
    style QR fill:#F59E0B,stroke:#D97706,color:#fff
    style UI fill:#EC4899,stroke:#DB2777,color:#fff
    style VER fill:#8B5CF6,stroke:#7C3AED,color:#fff
    style QA fill:#8B5CF6,stroke:#7C3AED,color:#fff
```

## 马斯克边界

马斯克有且只有**四项工作**。其他所有事情都交给子代理。

| 马斯克做的事 | 马斯克绝不做的事 |
|-----------------------|------------------------|
| 与用户对话 — 澄清需求、确认、交付 | 读源码来理解实现 |
| 管理状态 — state.json、需求文档、验收标准、计划 | 直接写代码或编辑代码 |
| 委派子代理 — 构建上下文包，通过 Agent 工具分发 | 跑测试、lint 或构建命令 |
| 综合结果 — 处理子代理返回状态，决定下一步 | 做代码审查或 UI 审查 |

这是硬规则，不是建议。如果你发现马斯克在做"绝不"列的事，那就是 bug。

## 为什么用子代理？

在一个长时间的 AI 编程会话中，主线程的上下文会随着每一轮对话膨胀：需求、代码差异、测试日志、审查意见、修复尝试、用户反馈、假设。经过几次上下文压缩后，AI 开始：

- **忘记原始目标** — 漂移到无关的工作
- **把假设当事实** — 未经验证的假设变成了"已知"
- **修改无关文件** — 失去范围追踪
- **声称完成但不验证** — 不检查验收标准就说"好了"

这不是模型能力问题。这是上下文管理问题。

Agent Workflow 通过分工解决它：

| 组件 | 保留在上下文中的内容 |
|-----------|----------------------|
| **马斯克** | 任务状态、用户决策、阶段摘要、证据、风险。保持轻量。 |
| **实现子代理** | 任务 + 目标 + 相关文件 + 非目标。做一件事，返回状态 + 证据。 |
| **规格审查员** | 需求 + 实际代码。逐行对比，返回带引用的通过/不通过。 |
| **代码质量审查员** | 代码 + 模式。检查结构，按严重级别返回问题。 |
| **验证子代理** | 变更文件 + 测试命令。跑测试，返回结果。 |
| **QA 子代理** | 验收标准 + 代码。逐条验证，返回每条标准的状态。 |

每个子代理收到一个 **SubagentContextPacket** — 自包含的提示词，包含：

- **任务：** 做什么
- **目标：** 成功条件
- **停止条件：** 什么时候停
- **相关文件：** 明确的文件列表
- **已知事实：** 来自需求、验收标准
- **非目标：** 不做什么
- **预期输出：** 写什么、写到哪里
- **验证预期：** 如何确认成功

子代理完成工作后返回：**状态、摘要、变更文件、证据、风险、下一步建议。** 没有对话历史泄漏。没有上下文膨胀。

多代理分工不是为了炫技。它让复杂任务在长上下文压力下**更稳定、更可控、更可审计、更不容易漂移**。

## 执行门控：什么时候问，什么时候继续

需求澄清是**判断门控**，不是审讯。马斯克遵循这条规则：

> **当缺失的答案可能实质性改变实现时，才提问。否则，记录假设并继续。**

| 情况 | 行动 |
|-----------|--------|
| 足够清晰，可以继续 | 开始工作 |
| 可以做低风险假设 | 记录假设，继续 |
| 歧义阻塞了实现 | 只问必要的问题 |
| 高风险 / 破坏性 / 安全 / 支付 / 迁移 | 生成需求 + 验收标准，请求明确批准 |

这适用于**所有任务类型**：后端、前端、重构、Bug 修复、基础设施。

## 工作流强度：用最轻的安全工作流

不是每个任务都需要完整的重任务流程。原则是：**用最轻的安全工作流。**

| 任务类型 | 工作流强度 | 运行内容 |
|-----------|-------------------|-----------|
| 文档、README、注释、提示词 | **最小** | 编辑文件，返回差异摘要。不需要需求/验收/计划/state.json，不需要子代理。 |
| 简单 Bug 修复、笔误、配置变更 | **轻量** | 快速澄清，实现 + 验证。跳过完整审查链。 |
| 功能、重构、多文件变更 | **重任务** | 完整流程：需求 → 验收 → 计划 → 实现 → 审查 → 验证 → QA。 |
| 安全、支付、认证、迁移、大型重构 | **重任务 + 明确批准** | 完整流程，实现前需要用户确认。 |

例如 — 本文档的优化就是纯文档任务。它不需要 `requirements.md`、`acceptance.md`、`plan.md`、`state.json` 或 QA 子代理。它只需要：编辑文件、展示差异、完成。

## 阶段流程

```mermaid
graph TD
    A["需求澄清"] --> B["需求文档"]
    B --> C["验收标准"]
    C --> D["执行计划"]
    D --> E["实现"]
    E --> F["规格合规审查"]
    F --> G["代码质量审查"]
    G --> H{"前端任务？"}
    H -->|是| I["UI 审查"]
    H -->|否| J["验证"]
    I --> J
    J --> K["QA"]
    K --> L["最终交付"]

    style A fill:#3B82F6,stroke:#2563EB,color:#fff
    style E fill:#10B981,stroke:#059669,color:#fff
    style F fill:#F59E0B,stroke:#D97706,color:#fff
    style G fill:#F59E0B,stroke:#D97706,color:#fff
    style I fill:#EC4899,stroke:#DB2777,color:#fff
    style J fill:#8B5CF6,stroke:#7C3AED,color:#fff
    style K fill:#8B5CF6,stroke:#7C3AED,color:#fff
    style L fill:#3B82F6,stroke:#2563EB,color:#fff
```

| 阶段 | 执行者 | 说明 |
|------|--------|------|
| `requirement_clarification` | 马斯克 | 与用户对话，消除歧义 |
| `requirements` | 马斯克 | 写 requirements.md，用户确认 |
| `acceptance` | 马斯克 | 写可测试的验收标准，用户确认 |
| `plan` | 马斯克 | 写可执行的任务分解 |
| `implementation` | 子代理 | 实现代码（高风险用 worktree 隔离） |
| `spec_compliance_review` | 子代理 | 读实际代码，逐条对比需求 |
| `code_quality_review` | 子代理 | 检查结构、正确性、可维护性 |
| `ui_review` | 子代理 | 抓 AI 味 — 字体、渐变、布局、响应式 |
| `verification` | 子代理 | 跑测试、lint、构建 |
| `qa` | 子代理 | 逐条验证验收标准 |
| `final_handoff` | 马斯克 | 带证据包向用户汇报 |

## 核心特性

| 特性 | 说明 |
|------|------|
| **马斯克-子代理分离** | 主线程协调，子代理执行。马斯克永远不写代码。 |
| **SubagentContextPacket** | 自包含提示词：任务、目标、文件、非目标、验证条件。不泄漏对话历史。 |
| **实现者四状态返回** | `DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED` — 马斯克处理每种状态 |
| **三阶段审查** | 规格合规 + 代码质量 + UI 审查（前端任务） |
| **执行门控** | 只在答案实质性影响实现时才提问；否则记录假设继续 |
| **工作流强度** | 最轻安全工作流 — 文档跳过重任务流程，简单修复跳过完整审查链 |
| **检查点 & 恢复** | 通过 handoff.md 在上下文重置后恢复。永远不从记忆恢复。 |
| **漂移检测** | 每个阶段后验证工作是否仍服务于原始意图 |
| **风险隔离** | 高风险任务用 git worktree 隔离；中风险共享工作目录 |

## 快速开始

### AI 辅助安装（推荐）

把这段话交给你的 AI 编程代理：

```text
请阅读 https://github.com/xzh20121116/agent-workflow，帮我全局安装 agent-workflow 技能。
```

### 手动安装

```bash
git clone https://github.com/xzh20121116/agent-workflow.git ~/.agent-workflow

# Claude Code:
ln -s ~/.agent-workflow/skills/agent-workflow-init ~/.claude/skills/agent-workflow-init
ln -s ~/.agent-workflow/skills/agent-workflow-start ~/.claude/skills/agent-workflow-start

# Codex App:
ln -s ~/.agent-workflow/skills/agent-workflow-init ~/.codex/skills/agent-workflow-init
ln -s ~/.agent-workflow/skills/agent-workflow-start ~/.codex/skills/agent-workflow-start
```

## 使用

### 初始化项目

```text
帮我用 agent-workflow 初始化当前项目
```

### 发起功能需求（重任务流程）

```text
用重任务流程处理：用户个人中心增加修改手机号功能
```

### 修复 Bug

```text
用重任务流程处理：支付回调偶发失败，大概一天出现几次
```

### 美化前端页面

```text
用重任务流程美化 src/pages/landing/index.tsx 页面
```

### 只做规格合规审查

```text
帮我审查 src/services/auth.service.ts 是否符合 docs/requirements.md 中的需求
```

### 只做代码质量审查

```text
帮我做代码质量审查：src/services/order.service.ts
```

## 包含的技能

| 技能 | 用途 |
|-------|---------|
| `agent-workflow-init` | 项目级初始化器。创建 `docs/agent/` 结构、AGENTS.md、项目配置。 |
| `agent-workflow-start` | 需求级入口。创建需求工作区，驱动从澄清到交付的完整流程。 |

### 子代理提示词模板

每个角色都有专用的提示词模板，位于 `skills/agent-workflow-start/references/`：

| 模板 | 角色 | 核心特点 |
|----------|------|-------------|
| `implementer-prompt.md` | 后端实现 | SubagentContextPacket、四状态返回 |
| `frontend-implementer-prompt.md` | 前端实现 | 设计约束（排版、配色、布局、动效） |
| `spec-reviewer-prompt.md` | 规格合规审查 | "不要相信报告" — 读实际代码 |
| `code-quality-reviewer-prompt.md` | 代码质量审查 | 结构、正确性、可维护性 |
| `ui-reviewer-prompt.md` | UI/视觉审查 | AI Slop Score、响应式检查、无障碍 |
| `verification-prompt.md` | 测试/lint/构建 | 运行项目测试套件 |
| `qa-prompt.md` | 验收标准 | 逐条验证验收条件 |

## 运行产物

一次成功的流程结束后，你会得到：

```
docs/agent/requests/REQ-20260609-001/
├── requirements.md          # 我们要做什么
├── acceptance.md            # 怎么验证它
├── plan.md                  # 任务分解
├── state.json               # 机器可读的状态
├── handoff.md               # 恢复检查点
├── implementation.md        # 做了什么，改了哪些文件
├── review.md                # 规格 + 代码质量审查结果
├── verification.md          # 测试结果、lint 输出
└── qa.md                    # 验收标准检查
```

每个声明都有证据支撑。没有"理论上应该可以"。

## 项目由来

Agent Workflow 来自**真实的日常使用** — 反复遇到同样的痛点：AI 代理不理解需求就开始乱写代码，主线程上下文膨胀导致目标漂移。

初始版本完成后，作者发现了 [Aegis](https://github.com/GanyuanRan/Aegis) 和 [Superpowers](https://github.com/obra/superpowers)。两者都有宝贵的想法。Agent Workflow 借鉴了它们的核心思路，并在此基础上做了简化和补充。

## Agent Workflow 的独有优势

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **主线程** | **永远不碰代码** | 协调者 + baseline | 自动触发 |
| **审查** | **三阶段**（规格 + 质量 + UI） | 两阶段 | 两阶段 |
| **实现者** | **四状态返回** | 子代理驱动 | 计划驱动 |
| **上下文** | **SubagentContextPacket**（隔离） | baseline 上下文 | 计划即初级工程师 |
| **执行门控** | 只在需要时提问，记录假设 | 改动前读 baseline | 统一流程 |
| **工作流强度** | 每类任务用最轻安全工作流 | 风险自适应 | 统一 |
| **安装** | **零配置** | doctor 脚本 | 逐宿主插件 |

### 核心优势：马斯克纪律

AI 编程代理处理复杂任务的头号失败模式：**主线程什么都干** — 又聊天又写代码又跑测试，上下文越来越长，压缩几次之后目标漂移，行为失控。

Agent Workflow 执行硬规则：**马斯克永远不读代码、不写代码、不跑测试。** 所有编码任务都交给子代理，每个子代理拿到自包含的上下文包。马斯克的上下文保持干净，子代理保持专注，不泄漏。

这适用于**所有任务类型**：后端 API、数据库迁移、代码重构、Bug 修复、基础设施变更，当然也包括前端。

### 核心优势：SubagentContextPacket

每个子代理拿到自包含的上下文包 — 任务、目标、文件、非目标、验证条件。没有对话历史泄漏。没有上下文膨胀。子代理干完活，返回证据。

### 核心优势：三阶段审查

其他工具两阶段审查。Agent Workflow 三阶段：

1. **规格合规** — 做对了吗？（读实际代码，逐条对比需求）
2. **代码质量** — 做好吗？（结构、正确性、可维护性）
3. **UI 审查** — 看着对吗？（前端任务：排版、布局、响应式、无障碍）

前两个适用于**所有任务**。第三个是前端的加分项。

### 加分项：前端质量控制

AI 生成的前端有一种"塑料感"。Agent Workflow 通过设计约束注入和 UI 审查员来解决。但这只是众多特性之一，不是核心卖点。

### 什么时候用 Agent Workflow

- 你希望主线程专注协调，不碰代码
- 你想要显式的状态处理（DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED）
- 你想要自包含的子代理执行，不泄漏上下文
- 你想要简单的安装和最少的配置
- 你想要经过验证的工作流模式，同时保持简单的安装和配置

### 什么时候用别的

- 复杂企业代码库，改动前需要 baseline 读取 → [Aegis](https://github.com/GanyuanRan/Aegis)
- TDD 优先团队，红-绿-重构不可妥协 → [Superpowers](https://github.com/obra/superpowers)

## 项目结构

```
.
├── skills/
│   ├── agent-workflow-init/
│   │   ├── SKILL.md
│   │   ├── references/agent-workflow-guide.md
│   │   ├── assets/templates/
│   │   │   ├── AGENTS.md.template
│   │   │   └── change-request-template.md
│   │   └── scripts/
│   │       ├── init_agent_workflow.py
│   │       └── install_symlinks.sh
│   └── agent-workflow-start/
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

## 致谢

- [Aegis](https://github.com/GanyuanRan/Aegis) — baseline-first、evidence-driven 的 AI 编程代理方法包
- [Superpowers](https://github.com/obra/superpowers) — Jesse Vincent 创建的可组合代理技能

## 许可证

MIT License。见 [LICENSE](LICENSE)。
