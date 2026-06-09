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

## Why Agent Workflow

When AI agents face complex tasks, they tend to:

- Do everything themselves instead of delegating
- Stop after requirements clarification instead of continuing
- Produce ugly, generic UI with obvious AI tells
- Skip verification and claim success without evidence

Agent Workflow solves this by turning the main thread into an **Orchestrator** that only talks to the user, manages state, and delegates work to specialized subagents. It never touches code directly.

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

## Usage

### 1. Initialize a project

After installation, tell your agent:

```text
帮我用 agent-workflow 初始化当前项目
```

Or use the skill directly: `/agent-workflow-init`

### 2. Start a request

```text
用重任务流程处理：用户个人中心增加修改手机号功能
```

The Orchestrator will clarify requirements, write acceptance criteria, get your confirmation, then automatically delegate to subagents through the full stage flow.

### 3. Frontend tasks (with design constraints)

```text
用重任务流程美化 src/pages/profile/index.tsx 页面
```

Frontend tasks automatically get design constraints and a UI review stage — no extra setup needed.

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

## Project Structure

```
.
├── skills/
│   ├── agent-workflow-init/          # Project-level bootstrapper
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   └── agent-workflow-guide.md
│   │   ├── assets/templates/
│   │   │   ├── AGENTS.md.template
│   │   │   └── change-request-template.md
│   │   └── scripts/
│   │       ├── init_agent_workflow.py
│   │       └── install_symlinks.sh
│   └── agent-workflow-start/         # Request-level entry point
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

## Risk-Based Subagent Policy

| Risk Level | Implementation | Reviews | Verification | Isolation |
|------------|---------------|---------|--------------|-----------|
| `critical` | Required | Spec + Code Quality + UI | Required | worktree |
| `high` | Required | Spec + Code Quality + UI | Required | worktree |
| `medium` | Required | Conditional | Required | shared |

## Comparison with Aegis & Superpowers

Agent Workflow is inspired by both [Aegis](https://github.com/GanyuanRan/Aegis) and [Superpowers](https://github.com/obra/superpowers), but takes a different approach. Here's how they compare:

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
| **Implementer status** | 4-status return (DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED) | Subagent-driven | Plan-driven |

### Frontend Capabilities

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **Frontend task detection** | Auto-detects .tsx/.vue/.html and UI-related keywords | Not included | Not included |
| **AI-slop detection** | Dedicated UI reviewer checks for Inter font, neon gradients, 3 equal columns, placeholder content | Not included | Not included |
| **Design system injection** | Typography, color, layout, motion, icon constraints in implementer prompt | Not included | Not included |
| **Responsive check** | 375px mobile, 768px tablet, 44px touch targets | Not included | Not included |

### Setup & Multi-Host

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **Setup complexity** | `git clone` + symlink, zero config | Guided prompt + `aegis-doctor.py` verification | Per-host plugin install |
| **Config surface** | Minimal (risk level per request) | Rich (activation mode, TDD mode, host registry) | Minimal |
| **Supported hosts** | Claude Code, Codex App (universal via SKILL.md) | 15+ hosts (many pending verification) | 7 hosts |
| **Verification tooling** | Manual (run tests in your project) | `aegis-doctor.py` with JSON health checks | Manual |

### Where Agent Workflow Excels

**Frontend-heavy projects.** Agent Workflow is the only one with built-in frontend design constraints and a dedicated UI review stage. If your AI agent generates ugly UI with Inter fonts, neon gradients, and 3-column layouts, Agent Workflow catches it before it ships.

**Orchestrator discipline.** The strict "Orchestrator never touches code" rule prevents the common problem where the main thread starts coding instead of delegating. Both Aegis and Superpowers trust the agent more; Agent Workflow trusts the process more.

**Simpler mental model.** Two skills (`init` + `start`), minimal config, no doctor scripts. You clone, symlink, and go.

**Implementer status clarity.** The 4-status return (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED) gives the Orchestrator explicit decision points instead of assuming success.

### Where Others Excel

**Aegis is better for:**
- Complex enterprise codebases requiring baseline reads before changes
- Teams that need risk-adaptive TDD (strict for risky, light for simple)
- Multi-host environments with 15+ different AI coding agents
- Bug fixes that need dual-track closure (repair + retirement)

**Superpowers is better for:**
- Teams that want strong TDD enforcement as non-negotiable discipline
- Projects where uniform process (no risk routing) is a feature, not a limitation
- Environments with many different host platforms (7 hosts)

### When to Use Which

| Scenario | Recommended |
|----------|-------------|
| Frontend + backend project with UI quality concerns | **Agent Workflow** |
| Complex legacy codebase, need baseline before changes | **Aegis** |
| TDD-first team, want strict red-green-refactor | **Superpowers** |
| Quick feature with minimal setup overhead | **Agent Workflow** |
| Multi-host team (10+ different AI agents) | **Aegis** |
| Want evidence-gated completion with risk tracking | **Aegis** |
| Need to prevent AI from generating ugly UI | **Agent Workflow** |
| Simple composable skills, no workflow overhead | **Superpowers** |

## Inspired By

- [Aegis](https://github.com/GanyuanRan/Aegis) — baseline-first, evidence-driven method pack for AI coding agents
- [Superpowers](https://github.com/obra/superpowers) — composable agent skills by Jesse Vincent

## License

MIT License. See [LICENSE](LICENSE).
