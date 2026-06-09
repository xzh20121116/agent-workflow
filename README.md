# Agent Workflow

Orchestrator-subagent workflow skills for AI coding agents. Turns your AI agent into a disciplined project manager that delegates work to specialized subagents instead of doing everything itself.

## What This Does

The main thread becomes an **Orchestrator** that:

1. Talks to you (requirement clarification, confirmations)
2. Manages state (writes requirements, acceptance, plan)
3. Delegates to subagents (implementation, review, verification, QA)
4. Reports results

The Orchestrator **never** touches code directly. Every coding task goes to an independent subagent.

## Key Features

- **Orchestrator-subagent separation** — main thread coordinates, subagents execute
- **SubagentContextPacket** — self-contained prompts, no conversation history leaking
- **Two-stage review** — spec compliance (did you build the right thing?) + code quality (did you build it well?)
- **UI review** — catches AI-generated UI problems (ugly fonts, neon gradients, generic layouts)
- **Frontend design constraints** — injects design rules into implementation prompts
- **Checkpoint & resume** — survives context resets, never resumes from memory alone
- **Implementer 4-status return** — DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED

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
├── LICENSE
└── README.md
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

- **Typography**: Banned Inter/Roboto/Arial, use Geist/Outfit/Satoshi
- **Color**: Max 1 accent, saturation < 80%, no neon/purple gradients
- **Layout**: No 3 equal columns, generous whitespace (py-24+), asymmetric grids
- **Components**: No rounded-full on large elements, no heavy shadows
- **Motion**: Custom cubic-bezier, respect prefers-reduced-motion
- **Content**: No placeholder names, no em-dashes, real copy only

## Inspired By

- [Aegis](https://github.com/GanyuanRan/Aegis) — method pack for AI coding agents
- [Superpowers](https://github.com/obra/superpowers) — composable agent skills

## License

MIT
