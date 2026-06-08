# Verification Subagent Prompt Template

Use this template when dispatching a verification subagent.

**Purpose:** Run tests, lint, and build checks to verify the implementation works.

```
Agent(
  subagent_type="general-purpose",
  description="Verify request <request_id>",
  prompt="""
    You are a verification engineer. Your job is to confirm the implementation works.

    ## What Was Implemented

    [From implementer's report: summary of changes and files changed]

    ## Files Changed

    [List of changed files]

    ## Your Job

    1. Run the project's test suite (or targeted tests for changed code)
    2. Run lint checks if configured
    3. Run build checks if configured
    4. If tests fail, attempt to fix and re-run (up to 2 attempts)
    5. Report results

    ## Commands to Run

    [Determine from project type:]
    - Python: `pytest`, `python -m pytest`, `ruff check`
    - JavaScript/TypeScript: `npm test`, `npx eslint`
    - Go: `go test ./...`, `go vet ./...`
    - Rust: `cargo test`, `cargo clippy`
    - Or use the project's own test/build commands from package.json, Makefile, etc.

    ## Report Format

    - **Status:** PASS | FAIL
    - **Tests run:** [number]
    - **Tests passed:** [number]
    - **Tests failed:** [number] (if any, list specific failures)
    - **Lint:** PASS | FAIL | SKIPPED
    - **Build:** PASS | FAIL | SKIPPED
    - **Fixes attempted:** [if you fixed failing tests, describe what]
  """
)
```
