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
    Orchestrator-subagent workflow skills for AI coding agents.<br/>
    Turns your AI agent into a disciplined project manager that delegates work to specialized subagents.
</p>

<p align="center">
    <a href="README.md"><strong>English</strong></a>
    ·
    <a href="README_zh-CN.md"><strong>中文</strong></a>
</p>

---

## The Problem

You give your AI agent a complex task: "add phone number change to the user profile." What happens next?

- It starts writing code without understanding the full requirement
- It implements the backend but forgets the frontend form
- The UI looks like every other AI-generated page: Inter font, purple gradient, 3 equal columns
- It says "done" without running a single test
- You ask "what about error handling?" and it starts over from scratch

**Agent Workflow fixes this.** It turns your AI agent into a disciplined project manager that delegates to specialized subagents — one implements, another reviews, another verifies. The main thread never touches code.

## How It Works in Practice

### Scenario 1: Full-Stack Feature — "Add phone number change"

You say:

```text
用重任务流程处理：用户个人中心增加修改手机号功能
```

**What happens next:**

```
You:  "需要支持哪些验证方式？短信验证码还是邮箱验证码？"
You:  "短信验证码"
You:  "旧手机号需要验证吗？"
You:  "需要"
Orchestrator writes requirements.md → you confirm
Orchestrator writes acceptance.md → you confirm
Orchestrator writes plan.md

── Orchestrator dispatches IMPLEMENTATION subagent ──
   Subagent reads plan, implements backend API + frontend form
   Returns: DONE (4 files changed, tests passing)

── Orchestrator dispatches SPEC COMPLIANCE REVIEWER ──
   Reviewer reads actual code, compares to requirements
   Result: PASS — all requirements covered

── Orchestrator dispatches CODE QUALITY REVIEWER ──
   Reviewer checks structure, error handling, patterns
   Result: PASS — 1 minor issue noted

── Orchestrator dispatches VERIFICATION subagent ──
   Runs tests, lint, build for changed files
   Result: PASS — 12 tests, 0 failures

── Orchestrator dispatches QA subagent ──
   Verifies every acceptance criterion against code
   Result: PASS — all 8 criteria satisfied

Orchestrator: "完成。修改手机号功能已实现，包含短信验证、旧手机验证、
60秒重发倒计时。共修改 4 个文件，通过全部 12 个测试。"
```

You never wrote a line of code. You answered 4 questions. The workflow did the rest.

### Scenario 2: Frontend Beautification — "This landing page is ugly"

You say:

```text
用重任务流程美化 src/pages/landing/index.tsx 页面
```

**What happens next:**

The Orchestrator detects this is a frontend task and automatically:
- Uses the **frontend implementer** with design constraints (typography, color, layout, motion rules)
- Adds a **UI review stage** after code quality review

```
── Orchestrator dispatches FRONTEND IMPLEMENTATION subagent ──
   Subagent implements with design constraints:
   - Font: Geist Sans instead of Inter
   - Color: warm off-black #2F3437, single accent #3B82F6
   - Layout: asymmetric grid, py-28 sections, no 3-equal-columns
   - Motion: cubic-bezier(0.16,1,0.3,1), respects reduced-motion
   Returns: DONE (3 files changed)

── Spec + Code Quality reviews pass ──

── Orchestrator dispatches UI REVIEWER ──
   AI Slop Score: 2/10 (was 8/10 before)
   - No banned fonts found ✓
   - No neon gradients ✓
   - No 3 equal columns ✓
   - Responsive on mobile/tablet ✓
   - Color contrast WCAG AA ✓
   Result: PASS
```

The UI reviewer catches problems that code review misses: ugly fonts, generic layouts, AI tells.

### Scenario 3: Bug Fix — "Payment callback fails intermittently"

You say:

```text
用重任务流程处理：支付回调偶发失败，大概一天出现几次
```

**What happens next:**

```
Orchestrator: "回调失败时有错误日志吗？"
You:  "有，显示 timeout"
Orchestrator: "第三方支付平台的超时设置是多少？"
You:  "5秒"
Orchestrator: "我们的回调处理平均耗时？"
You:  "不确定，但有数据库写入操作"

Orchestrator writes requirements (root cause analysis + fix)

── Implementation subagent investigates ──
   Finds: callback handler does synchronous DB write,
   occasionally exceeds 5s under load
   Fix: async DB write + response-first pattern
   Returns: DONE_WITH_CONCERNS
     "Concern: the async write means callback returns success
      before DB is updated. Need idempotency check."

Orchestrator reads concern, decides it's valid, adds
idempotency requirement to the plan

── Re-dispatches implementation with updated requirements ──
   Returns: DONE

── Reviews, verification, QA all pass ──
```

The `DONE_WITH_CONCERNS` status lets the subagent flag doubts without blocking. The Orchestrator decides whether to address them.

### Scenario 4: Refactoring — "This service file is 800 lines"

You say:

```text
用重任务流程重构 src/services/order.service.ts，太臃肿了
```

**What happens next:**

```
Orchestrator: "拆分的目标是什么？按业务领域还是按技术层次？"
You:  "按业务领域，把订单、支付、通知拆开"
Orchestrator: "现有的测试覆盖情况？"
You:  "有单元测试，覆盖率约 60%"

Orchestrator writes plan: split into 3 services + shared types

── Implementation subagent works in worktree (high-risk) ──
   Splits order.service.ts into:
   - order.service.ts (order CRUD)
   - payment.service.ts (payment processing)
   - notification.service.ts (email/SMS/webhook)
   - shared/types.ts (common types)
   Returns: DONE (1 file deleted, 4 files created)

── Spec compliance reviewer ──
   Checks: all original functions still available?
   Result: PASS — public API unchanged

── Code quality reviewer ──
   Checks: clear boundaries? circular deps?
   Result: PASS — clean separation

── Verification subagent ──
   Runs existing tests against refactored code
   Result: PASS — all 24 tests still pass

── QA subagent ──
   Verifies: no breaking changes to external consumers
   Result: PASS
```

High-risk tasks automatically use **worktree isolation** — the refactoring happens in an isolated branch, never touching your working directory until it's verified.

## Core Architecture

```
User ←→ Orchestrator (main thread)
              │
              ├── Implementation Subagent
              ├── Spec Compliance Reviewer
              ├── Code Quality Reviewer
              ├── UI Reviewer (frontend tasks)
              ├── Verification Subagent
              └── QA Subagent
```

The Orchestrator has exactly **four jobs**:

1. **Talk to the user** — requirement clarification, confirmations, final handoff
2. **Manage state** — read/write state.json, requirements, acceptance, plan
3. **Dispatch subagents** — build self-contained SubagentContextPacket, delegate via Agent tool
4. **Synthesize results** — handle implementer status, decide next action

The Orchestrator **never** reads source code, runs tests, writes implementation, or performs review directly.

## Key Features

| Feature | Description |
|---------|-------------|
| **Orchestrator-subagent separation** | Main thread coordinates, subagents execute. No self-coding. |
| **SubagentContextPacket** | Self-contained prompts with task, goal, files, non-goals, verification. No conversation history leaking. |
| **Two-stage review** | Spec compliance (did you build the right thing?) + code quality (did you build it well?) |
| **UI review** | Catches AI-generated UI problems: ugly fonts, neon gradients, generic layouts. AI Slop Score 0-10. |
| **Frontend design constraints** | Injects typography, color, layout, and motion rules into implementation prompts. |
| **Implementer 4-status return** | DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED — Orchestrator handles each appropriately. |
| **Checkpoint & resume** | Survives context resets via handoff.md. Never resumes from memory alone. |
| **Drift detection** | After each stage, verifies work still serves original intent. |

## Stage Flow

```
requirement_clarification  (Orchestrator talks to user)
→ requirements             (Orchestrator writes requirements.md)
→ acceptance               (Orchestrator writes acceptance.md, user confirms)
→ plan                     (Orchestrator writes plan.md)
→ implementation           (Subagent implements, worktree if high-risk)
→ spec_compliance_review   (Subagent: did you build the right thing?)
→ code_quality_review      (Subagent: is the code well-built?)
→ ui_review                (Subagent: frontend tasks only, catches AI slop)
→ verification             (Subagent: runs tests, lint, build)
→ qa                       (Subagent: verifies acceptance criteria)
→ final_handoff            (Orchestrator reports to user)
```

## Installation

Paste this to your AI coding agent:

```text
请阅读 https://github.com/xzh20121116/agent-workflow，帮我全局安装 agent-workflow 技能。
```

## Subagent Prompt Templates

Each role has a dedicated prompt template in `skills/agent-workflow-start/references/`:

| Template | Role | Key Feature |
|----------|------|-------------|
| `implementer-prompt.md` | Backend implementation | SubagentContextPacket, 4-status return |
| `frontend-implementer-prompt.md` | Frontend implementation | Design constraints (typography, color, layout, motion) |
| `spec-reviewer-prompt.md` | Spec compliance review | "Do Not Trust the Report" directive |
| `code-quality-reviewer-prompt.md` | Code quality review | Structure, correctness, maintainability |
| `ui-reviewer-prompt.md` | UI/visual review | AI-slop detection, responsive check, accessibility |
| `verification-prompt.md` | Test/lint/build | Runs project test suite |
| `qa-prompt.md` | Acceptance criteria | Verifies every criterion against code |

## Design Constraints (Frontend)

The `frontend-implementer-prompt.md` injects these rules to prevent ugly AI-generated UI:

| Category | Rules |
|----------|-------|
| **Typography** | Banned Inter/Roboto/Arial. Use Geist/Outfit/Satoshi. Text color never #000000. |
| **Color** | Max 1 accent, saturation < 80%. No neon/purple gradients. |
| **Layout** | No 3 equal columns. Generous whitespace (py-24+). Asymmetric grids. |
| **Components** | No rounded-full on large elements. No heavy shadows. |
| **Motion** | Custom cubic-bezier. Respect prefers-reduced-motion. |
| **Content** | No placeholder names. No em-dashes. Real copy only. |

## Risk-Based Subagent Policy

| Risk Level | Implementation | Reviews | Verification | Isolation |
|------------|---------------|---------|--------------|-----------|
| `critical` | Required | Spec + Code Quality + UI | Required | worktree |
| `high` | Required | Spec + Code Quality + UI | Required | worktree |
| `medium` | Required | Conditional | Required | shared |

## Comparison with Aegis & Superpowers

Agent Workflow is inspired by both [Aegis](https://github.com/GanyuanRan/Aegis) and [Superpowers](https://github.com/obra/superpowers), but takes a different approach.

### Architecture

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **Core model** | Orchestrator-subagent with strict separation | Baseline-first method pack with risk routing | Composable auto-triggered skills |
| **Main thread role** | Coordinator only — never touches code | Coordinator with baseline-read phase | Skills auto-trigger based on task |
| **Subagent dispatch** | SubagentContextPacket (self-contained) | Subagent-driven with baseline context | Subagent-driven, plan-as-junior-engineer |
| **Risk routing** | 3 levels (critical/high/medium) with escalating isolation | Low/medium/high complexity routing | Uniform process for all tasks |
| **TDD enforcement** | Optional (project decides) | Risk-adaptive (strict/light/skip) | Strict RED-GREEN-REFACTOR |

### Review & Verification

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **Review stages** | Spec compliance → Code quality → UI review | Baseline + two-stage review | Two-stage code review |
| **UI/Frontend review** | Dedicated UI reviewer with AI Slop Score (0-10) | Not included | Not included |
| **Design constraints** | Built-in frontend design rules (typography, color, layout, motion) | Not included | Not included |
| **Completion gate** | Evidence bundle + QA verification | Evidence-gated with residual risk tracking | Evidence over claims |

### Where Agent Workflow Excels

**Frontend-heavy projects.** Agent Workflow is the only one with built-in frontend design constraints and a dedicated UI review stage. If your AI agent generates ugly UI with Inter fonts, neon gradients, and 3-column layouts, Agent Workflow catches it before it ships.

**Orchestrator discipline.** The strict "Orchestrator never touches code" rule prevents the common problem where the main thread starts coding instead of delegating. Both Aegis and Superpowers trust the agent more; Agent Workflow trusts the process more.

**Simpler mental model.** Two skills (`init` + `start`), minimal config, no doctor scripts. You clone, symlink, and go.

### Where Others Excel

**Aegis** is better for complex enterprise codebases needing baseline reads, risk-adaptive TDD, and multi-host support (15+ agents).

**Superpowers** is better for TDD-first teams that want strict red-green-refactor as non-negotiable discipline.

### When to Use Which

| Scenario | Recommended |
|----------|-------------|
| Frontend + backend project with UI quality concerns | **Agent Workflow** |
| Complex legacy codebase, need baseline before changes | **Aegis** |
| TDD-first team, want strict red-green-refactor | **Superpowers** |
| Quick feature with minimal setup overhead | **Agent Workflow** |
| Need to prevent AI from generating ugly UI | **Agent Workflow** |

## Inspired By

- [Aegis](https://github.com/GanyuanRan/Aegis) — baseline-first, evidence-driven method pack for AI coding agents
- [Superpowers](https://github.com/obra/superpowers) — composable agent skills by Jesse Vincent

## License

MIT License. See [LICENSE](LICENSE).
