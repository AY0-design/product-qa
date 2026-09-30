# product-qa

A senior QA engineer in skill form. **product-qa** helps Claude think in risk, failure modes and release readiness, instead of just producing lists of happy-path test cases.

## What it does

- **Post-build QA pass (runs by itself):** when Claude finishes building a feature, it:
  - runs your existing tests and linters
  - writes tests for the riskiest failure paths (duplicates, retries, authorization, concurrency, money precision)
  - fixes what breaks
  - gives a verdict: `READY / CONDITIONAL / NOT READY / INSUFFICIENT INFORMATION`
- **Test strategy:** risk-ranked plans with test layers, failure scenarios, exploratory missions, release gates and observability needs.
- **Release readiness:** "212 tests pass" is never taken as enough on its own. It fills in a proper release gate.
- **Bugs and flaky tests:** structured failure investigation and actionable bug reports.
- **Test and PR review:** judges tests on fidelity, resilience and precision.

It includes extra checks for web, mobile, API, background jobs, AI and **financial** products (idempotency, reconciliation, kobo/decimal precision, webhooks). It also has stack hints for Flutter, NestJS, Supabase/Postgres, BullMQ and Nigerian payment providers (Paystack, Flutterwave, Monnify).

## Install

**Claude Code (plugin marketplace)**
```
/plugin marketplace add AY0-design/product-qa
/plugin install product-qa@product-qa
```

**Any agent that supports Agent Skills (via skills.sh)**
```
npx skills add AY0-design/product-qa
```

**Manual (Claude Code)**: copy `skills/product-qa` into `~/.claude/skills/` (personal) or `.claude/skills/` (per project).

**Claude.ai / Claude desktop**: download `product-qa.skill` (or a zip of `skills/product-qa`) from [Releases](../../releases) and upload it under **Settings → Capabilities → Skills**.

## Usage

You don't need to call it. It triggers when Claude finishes building something, or when you ask things like:

- "How should I test the new transfer flow?"
- "Is v2.4 ready to ship Friday?"
- "This test passes locally but fails in CI"
- "Write this up as a bug"

## Structure

```
skills/product-qa/
├── SKILL.md                  # core workflow, modes, output formats
└── references/
    ├── checklists.md         # edge cases, UX states, dependencies, data integrity, security
    ├── domain-modes.md       # web, mobile, API, jobs, AI, financial
    ├── templates.md          # test case, bug report, severity, release gate, flaky tests
    └── stack.md              # Flutter, NestJS, Supabase, BullMQ, Nigerian fintech
```

## License

MIT
