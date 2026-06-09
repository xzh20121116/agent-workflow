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

## 你遇到过这些问题吗？

你给 AI 代理一个任务："用户个人中心增加修改手机号功能"。然后：

- 它不问清楚就开始写代码，结果漏了旧手机号验证
- 后端写完了，前端表单忘做了
- 生成的 UI 满屏 Inter 字体 + 紫色渐变 + 三等分卡片，一看就是 AI 味
- 跑都没跑就说"已完成"，你一追问又从头来
- 上下文一长就"失忆"，之前讨论的全忘了

**Agent Workflow 就是为了解决这些问题。** 它把主线程变成一个编排器（Orchestrator），只跟你对话、管状态、派活。代码？子代理写。测试？子代理跑。审查？子代理审。编排器自己一行代码都不碰。

## 实际场景演示

### 场景 1：全栈功能 —— "加个修改手机号"

你说：

```text
用重任务流程处理：用户个人中心增加修改手机号功能
```

**接下来发生的事：**

```
编排器: "需要支持哪些验证方式？短信验证码还是邮箱验证码？"
你:     "短信验证码"
编排器: "旧手机号需要先验证吗？"
你:     "需要"
编排器: "新手机号需要二次确认吗？"
你:     "要，输入两次"
编排器: "发送频率有限制吗？"
你:     "60 秒冷却"

── 编排器写 requirements.md，你确认 ──
── 编排器写 acceptance.md，你确认 ──
── 编排器写 plan.md ──

── 委派【实现子代理】──
   子代理读取计划，实现后端 API + 前端表单
   返回：DONE（修改 4 个文件，测试通过）

── 委派【规格合规审查】──
   审查员读实际代码，逐条对比需求
   结果：PASS — 需求全部覆盖

── 委派【代码质量审查】──
   审查员检查结构、错误处理、代码规范
   结果：PASS — 1 个建议（非阻塞）

── 委派【验证子代理】──
   跑测试、lint、构建
   结果：PASS — 12 个测试，0 失败

── 委派【QA 子代理】──
   逐条验证验收标准
   结果：PASS — 8 条标准全部满足

编排器: "完成。修改手机号功能已实现：
- 短信验证码验证
- 旧手机号验证
- 新手机号二次确认
- 60 秒重发倒计时
共修改 4 个文件，通过 12 个测试。"
```

你全程只回答了 4 个问题。从需求到上线，代码一行没碰。

### 场景 2：前端美化 —— "这个页面太丑了"

你说：

```text
用重任务流程美化 src/pages/landing/index.tsx 页面
```

**编排器自动识别这是前端任务：**

```
── 委派【前端实现子代理】（带设计约束）──
   子代理按设计规范实现：
   - 字体：Geist Sans，禁用 Inter
   - 配色：暖灰 #2F3437，单一强调色 #3B82F6
   - 布局：非对称网格，py-28 留白，禁用三等分列
   - 动效：cubic-bezier(0.16,1,0.3,1)，尊重 reduced-motion
   返回：DONE（修改 3 个文件）

── 规格合规 + 代码质量审查通过 ──

── 委派【UI 审查员】──
   AI Slop Score：2/10（之前是 8/10）
   ✓ 没有禁用字体
   ✓ 没有霓虹渐变
   ✓ 没有三等分列
   ✓ 手机端响应式正常
   ✓ 颜色对比度 WCAG AA 达标
   结果：PASS
```

UI 审查员能抓住代码审查发现不了的问题：丑字体、通用布局、AI 味道。

### 场景 3：Bug 修复 —— "支付回调偶发失败"

你说：

```text
用重任务流程处理：支付回调偶发失败，大概一天出现几次
```

**编排器先排查：**

```
编排器: "回调失败时有错误日志吗？"
你:     "有，显示 timeout"
编排器: "第三方支付平台的超时设置是多少？"
你:     "5 秒"
编排器: "我们的回调处理平均耗时？"
你:     "不确定，但有数据库写入操作"

── 编排器写需求：定位根因 + 修复 ──

── 委派【实现子代理】调查 ──
   发现：回调处理同步写数据库，负载高时偶尔超过 5 秒
   修复：异步写入 + 先返回成功 + 幂等校验
   返回：DONE_WITH_CONCERNS
     "注意：异步写入意味着回调返回成功时数据库还没更新。
      需要确认幂等性是否足够。"

编排器读取顾虑，认为合理，把幂等校验加入需求

── 重新委派实现子代理 ──
   返回：DONE

── 审查、验证、QA 全部通过 ──
```

`DONE_WITH_CONCERNS` 状态让子代理可以提出疑虑而不阻塞流程。编排器决定是否处理。

### 场景 4：代码重构 —— "这个文件 800 行太臃肿了"

你说：

```text
用重任务流程重构 src/services/order.service.ts，太臃肿了
```

**编排器确认方向：**

```
编排器: "拆分目标是什么？按业务领域还是技术层次？"
你:     "按业务领域，把订单、支付、通知拆开"
编排器: "现有测试覆盖情况？"
你:     "有单元测试，覆盖率约 60%"

── 编排器写计划：拆成 3 个服务 + 共享类型 ──

── 委派【实现子代理】（在 worktree 中隔离工作）──
   将 order.service.ts 拆分为：
   - order.service.ts（订单 CRUD）
   - payment.service.ts（支付处理）
   - notification.service.ts（邮件/短信/webhook）
   - shared/types.ts（公共类型）
   返回：DONE（删除 1 个文件，创建 4 个文件）

── 规格合规审查 ──
   检查：原文件的所有函数是否仍然可用？
   结果：PASS — 公共 API 不变

── 代码质量审查 ──
   检查：边界清晰？循环依赖？
   结果：PASS — 分离干净

── 验证子代理 ──
   用原有测试跑重构后的代码
   结果：PASS — 24 个测试全部通过

── QA 子代理 ──
   验证：外部调用方无破坏性变更
   结果：PASS
```

高风险任务自动使用 **worktree 隔离** —— 重构在独立分支中进行，验证通过前不会碰你的工作目录。

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

把下面这段话交给你的 AI 编程代理：

```text
请阅读 https://github.com/xzh20121116/agent-workflow，帮我全局安装 agent-workflow 技能。
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

## 与 Aegis、Superpowers 的对比

Agent Workflow 的灵感来自 [Aegis](https://github.com/GanyuanRan/Aegis) 和 [Superpowers](https://github.com/obra/superpowers)，但走了一条不同的路。

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

### Agent Workflow 的优势

**前端项目。** 三者中唯一内置前端设计约束和 UI 审查阶段的。AI 代理生成的 Inter 字体 + 霓虹渐变 + 三等分布局，能在上线前抓住。

**编排器纪律。** 严格的"编排器永远不碰代码"规则。Aegis 和 Superpowers 更信任代理；Agent Workflow 更信任流程。

**更简单的心智模型。** 两个 skill，最小配置，不需要 doctor 脚本。

### 其他工具的优势

**Aegis** 更适合复杂企业级代码库（需要 baseline 读取）、风险自适应 TDD、多宿主环境（15+ 种代理）。

**Superpowers** 更适合 TDD 优先团队，把红-绿-重构作为不可妥协的纪律。

### 选择指南

| 场景 | 推荐 |
|------|------|
| 前端 + 后端项目，关注 UI 质量 | **Agent Workflow** |
| 复杂遗留代码库，改动前需要 baseline | **Aegis** |
| TDD 优先团队，要严格的红-绿-重构 | **Superpowers** |
| 快速实现功能，最小安装开销 | **Agent Workflow** |
| 需要防止 AI 生成丑陋 UI | **Agent Workflow** |

## 致谢

- [Aegis](https://github.com/GanyuanRan/Aegis) — 面向 AI 编程代理的 baseline-first、evidence-driven 工作流方法包
- [Superpowers](https://github.com/obra/superpowers) — Jesse Vincent 创建的可组合代理技能

## 许可证

MIT License。见 [LICENSE](LICENSE)。
