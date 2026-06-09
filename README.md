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

### Claude Code

```bash
# Clone to skills directory
git clone https://github.com/xzh20121116/agent-workflow.git ~/.claude/skills/agent-workflow

# Or symlink from a central location
git clone https://github.com/xzh20121116/agent-workflow.git ~/.agent-workflow
ln -s ~/.agent-workflow/skills/agent-workflow-init ~/.claude/skills/agent-workflow-init
ln -s ~/.agent-workflow/skills/agent-workflow-start ~/.claude/skills/agent-workflow-start
```

### Codex App

```bash
# Clone to skills directory
git clone https://github.com/xzh20121116/agent-workflow.git ~/.codex/skills/agent-workflow

# Or symlink
git clone https://github.com/xzh20121116/agent-workflow.git ~/.agent-workflow
ln -s ~/.agent-workflow/skills/agent-workflow-init ~/.codex/skills/agent-workflow-init
ln -s ~/.agent-workflow/skills/agent-workflow-start ~/.codex/skills/agent-workflow-start
```

### Universal (any host)

```bash
git clone https://github.com/xzh20121116/agent-workflow.git ~/.agent-workflow

# Then symlink or copy the skills to your host's skill directory
# Claude Code: ~/.claude/skills/
# Codex: ~/.codex/skills/
# Others: check your host's skill discovery path
```

## Usage

### 1. Initialize a project

```
/agent-workflow-init
```

Or explicitly:

```bash
python skills/agent-workflow-init/scripts/init_agent_workflow.py --project-root .
```

### 2. Start a request

```
用重任务流程处理：用户个人中心增加修改手机号功能
```

Or explicitly:

```bash
python skills/agent-workflow-start/scripts/start_agent_workflow.py --project-root . --title "修改手机号功能" --risk-level medium
```

### 3. Frontend tasks (with design constraints)

```
用重任务流程美化 src/pages/profile/index.tsx 页面
```

Frontend tasks automatically:
- Use `frontend-implementer-prompt.md` with design constraints
- Add a UI review stage after code quality review
- Check for AI-slop patterns (Inter font, neon gradients, 3 equal columns, etc.)

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

## Inspired By

- [Aegis](https://github.com/GanyuanRan/Aegis) — baseline-first, evidence-driven method pack for AI coding agents
- [Superpowers](https://github.com/obra/superpowers) — composable agent skills by Jesse Vincent

## License

MIT License. See [LICENSE](LICENSE).
