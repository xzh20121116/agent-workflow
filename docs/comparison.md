# Agent Workflow vs Aegis vs Superpowers

A detailed comparison of three AI coding agent workflow tools.

## Overview

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **Repo** | [xzh20121116/agent-workflow](https://github.com/xzh20121116/agent-workflow) | [GanyuanRan/Aegis](https://github.com/GanyuanRan/Aegis) | [obra/superpowers](https://github.com/obra/superpowers) |
| **Core model** | Orchestrator-subagent with strict separation | Baseline-first method pack with risk routing | Composable auto-triggered skills |
| **Philosophy** | Trust the process, not the agent | Evidence before claims, baseline before code | TDD + systematic process + complexity reduction |

## Architecture

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **Main thread role** | Coordinator only — never touches code | Coordinator with baseline-read phase | Skills auto-trigger based on task |
| **Subagent dispatch** | SubagentContextPacket (self-contained) | Subagent-driven with baseline context | Subagent-driven, plan-as-junior-engineer |
| **Risk routing** | 3 levels (critical/high/medium) with escalating isolation | Low/medium/high complexity routing | Uniform process for all tasks |
| **TDD enforcement** | Optional (project decides) | Risk-adaptive (strict/light/skip) | Strict RED-GREEN-REFACTOR |
| **Isolation model** | git worktree for high/critical risk | Baseline-read before changes | Plan-driven execution |

## Review & Verification

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **Review stages** | Spec compliance → Code quality → UI review | Baseline + two-stage review | Two-stage code review |
| **UI/Frontend review** | Dedicated UI reviewer with AI Slop Score (0-10) | Not included | Not included |
| **Design constraints** | Built-in frontend design rules (typography, color, layout, motion) | Not included | Not included |
| **Completion gate** | Evidence bundle + QA verification | Evidence-gated with residual risk tracking | Evidence over claims |
| **Implementer status** | 4-status return (DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED) | Subagent-driven | Plan-driven |

## Frontend Capabilities

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **Frontend task detection** | Auto-detects .tsx/.vue/.html and UI-related keywords | Not included | Not included |
| **AI-slop detection** | Dedicated UI reviewer checks for Inter font, neon gradients, 3 equal columns, placeholder content | Not included | Not included |
| **Design system injection** | Typography, color, layout, motion, icon constraints in implementer prompt | Not included | Not included |
| **Responsive check** | 375px mobile, 768px tablet, 44px touch targets | Not included | Not included |
| **Accessibility check** | WCAG AA contrast, focus states, alt text | Not included | Not included |

## Setup & Multi-Host

| | Agent Workflow | Aegis | Superpowers |
|---|---|---|---|
| **Setup complexity** | `git clone` + symlink, zero config | Guided prompt + `aegis-doctor.py` verification | Per-host plugin install |
| **Config surface** | Minimal (risk level per request) | Rich (activation mode, TDD mode, host registry) | Minimal |
| **Supported hosts** | Claude Code, Codex App (universal via SKILL.md) | 15+ hosts (many pending verification) | 7 hosts |
| **Verification tooling** | Manual (run tests in your project) | `aegis-doctor.py` with JSON health checks | Manual |

## Where Each Tool Excels

### Agent Workflow

**Frontend-heavy projects.** The only tool with built-in frontend design constraints and a dedicated UI review stage. If your AI agent generates ugly UI with Inter fonts, neon gradients, and 3-column layouts, Agent Workflow catches it before it ships.

**Orchestrator discipline.** The strict "Orchestrator never touches code" rule prevents the common problem where the main thread starts coding instead of delegating.

**Simpler mental model.** Two skills (`init` + `start`), minimal config, no doctor scripts.

**Implementer status clarity.** The 4-status return gives the Orchestrator explicit decision points instead of assuming success.

### Aegis

**Complex enterprise codebases.** Baseline reads before changes ensure the agent understands existing patterns, dependencies, and constraints before modifying code.

**Risk-adaptive TDD.** Strict TDD for risky changes, light verification for simple edits, skip TDD where inappropriate.

**Multi-host support.** Targets 15+ hosts with per-host install guides and a compatibility matrix.

**Dual-track closure.** Bug fixes document both the repair path and the retirement path for old code.

### Superpowers

**TDD-first teams.** Strict RED-GREEN-REFACTOR as non-negotiable discipline. Code written before tests gets deleted.

**Composable skills.** Clean, opinionated framework with strong process enforcement across common AI coding agents.

**Uniform process.** No risk routing — every task gets the same disciplined treatment.

## When to Use Which

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

## Can They Work Together?

Agent Workflow and Aegis/Superpowers solve different layers of the same problem. In theory:

- Aegis's baseline-read could feed into Agent Workflow's SubagentContextPacket
- Superpowers's TDD discipline could be enforced within Agent Workflow's implementation stage
- Agent Workflow's UI reviewer could complement any tool that lacks frontend awareness

However, they are currently designed as independent, standalone skill packs. Using multiple simultaneously would require manual integration.
