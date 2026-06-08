# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent.

**Purpose:** Verify the implementation is well-built (clean, tested, maintainable).

**Only dispatch after spec compliance review passes.**

```
Agent(
  subagent_type="general-purpose",
  description="Code quality review for request <request_id>",
  prompt="""
    You are reviewing code quality for an implementation.

    ## What Was Implemented

    [From implementer's report: summary of changes]

    ## What Was Requested

    [From plan.md: the task specification]

    ## Files Changed

    [List of files the implementer changed]

    ## Your Job

    Review the code for quality. Focus on:

    **Structure:**
    - Does each file have one clear responsibility with a well-defined interface?
    - Are units decomposed so they can be understood and tested independently?
    - Is the implementation following the file structure from the plan?
    - Did this implementation create new files that are already large?

    **Correctness:**
    - Are there obvious bugs or logic errors?
    - Are edge cases handled?
    - Is error handling appropriate?

    **Maintainability:**
    - Are names clear and accurate?
    - Is the code clean and readable?
    - Does it follow existing patterns in the codebase?

    **Testing:**
    - Are there tests for the new code?
    - Do tests verify behavior (not just mock behavior)?
    - Are tests comprehensive?

    ## Report Format

    - **Strengths:** What was done well
    - **Issues:**
      - Critical: Must fix before merge
      - Important: Should fix
      - Minor: Nice to fix
    - **Assessment:** Overall quality assessment
  """
)
```
