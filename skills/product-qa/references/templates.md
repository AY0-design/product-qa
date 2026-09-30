# QA Templates

## Contents
1. Test case
2. Automation classification
3. Bug report
4. Severity scale
5. Failure investigation
6. Flaky tests
7. Failure flows (API failure, partial completion, network failure)
8. Release gate
9. Regression loop
10. Quality metrics

---

## 1. Test case
One test should prove one meaningful behaviour.

```text
ID:
Title:
Risk:
Priority:
Preconditions:

Steps:
1.
2.
3.

Expected Result:
Actual Result:            (leave blank until executed)
Test Layer:               Unit / Integration / API-Contract / Component / E2E / Exploratory
Automation Candidate:     AUTOMATE / MANUAL / EXPLORATORY / NOT WORTH TESTING
```

## 2. Automation classification
- **AUTOMATE** when the test is repetitive, deterministic, high-value, frequently run, regression-sensitive, or expensive to do by hand.
- **MANUAL / EXPLORATORY** when it needs human judgement, is highly visual, requirements are still uncertain, or automation costs more than it returns.
- **NOT WORTH TESTING** when the risk is negligible. Say so explicitly, so it's a decision rather than an omission.

## 3. Bug report

```text
Title:              (specific behaviour, e.g. "Retrying a timed-out transfer creates a second debit instead of returning the original transaction")
Environment:
Build / Version:
Preconditions:
Steps to Reproduce:
1.
2.
3.
Expected Result:
Actual Result:
Frequency:          (always / intermittent x/y / once)
Severity:
Affected Users:
Evidence:           logs, screenshots, API responses, request IDs, timestamps
Suspected Area:
Regression Test Required:  (what test, at which layer)
```

Avoid "feature doesn't work". Name the exact behaviour that diverged.

## 4. Severity scale
Severity reflects impact, not how hard the bug is to fix.
- **Critical:** data loss, unauthorized access, financial loss, duplicate financial transaction, system-wide outage, critical security vulnerability.
- **High:** major workflow blocked, many users affected, important data incorrect, significant functionality unavailable.
- **Medium:** important feature degraded but a workaround exists, or a limited population is affected.
- **Low:** minor visual, copy or cosmetic issue, non-critical inconvenience.

## 5. Failure investigation

```text
Failure → What failed? → Expected vs actual → First observable divergence
→ Affected component → Failure category → Evidence → Reproduction
→ Severity → Recommended investigation / fix
```

Categories: product defect · test defect · environment defect · infrastructure failure · data issue · dependency failure · flaky test · unknown. Don't assume every failure is a product bug. Show the evidence for the category you pick.

## 6. Flaky tests
A test that fails then passes has not passed. It is flaky. Investigate: timing and fixed sleeps · race conditions · network · shared state between tests · test ordering · environment instability · un-awaited async work · random or time-dependent data · real external dependencies.

Then: identify the root cause, fix the test, product or environment, add monitoring, and track the flake rate. Quarantine only temporarily, with an owner and a date.

## 7. Failure flows

**API failure:** request → timeout or error → system detects it → user gets appropriate feedback → retry only if safe → no duplicate operation → recover → verify final state.

**Partial completion:** step 1 succeeds → step 2 fails → system detects the partial state → rollback or resume → user gets an accurate status → system stays consistent.

**Network failure:** user action → disconnect → request state unknown → system determines whether the operation completed (status check or idempotency key) → retry safely → no duplicate → show the final state.

## 8. Release gate

```text
Release Status:         READY / NOT READY / CONDITIONAL
Critical Risks:
Open Critical Issues:
Open High Issues:
Regression Status:
Performance Status:
Security Status:
Data Integrity Status:
Observability Status:   (logs, request IDs, metrics, alerts, audit)
Rollback Plan:          (feature flag? reversible migration? previous build?)
Known Limitations:
Recommended Action:
```

Readiness checklist:
- **Functional:** critical workflows pass, regression suite passes, no open critical defects.
- **Reliability:** no unacceptable flaky tests; retry and recovery verified.
- **Performance:** critical operations meet agreed thresholds; no regression.
- **Security:** applicable scenarios pass; authorization verified; sensitive data protected.
- **Data:** migrations verified (forward and rollback); integrity verified.
- **UX:** critical flows understandable; errors actionable; states communicated.
- **Production:** logging, monitoring, alerts, rollback, feature flag where appropriate; support and ops know about behaviour changes.

Never base the recommendation on test count alone.

## 9. Regression loop
Every production defect raises the question: what test would stop this from coming back?

```text
Production bug → root cause → regression test at the lowest effective layer → runs in CI
```

## 10. Quality metrics
Don't use test count as the primary metric. Track:
- **Defects:** escaped defects, critical defects, reopen rate, defect age, regression defects.
- **Automation:** critical-journey coverage, suite execution time, flake rate, time to investigate failures.
- **Delivery:** change failure rate, rollback rate, release-blocking defects, code-complete-to-release time.
- **Product:** crash rate, API error rate, failed transaction rate, latency, user-facing failure rate.

The real question: how well did testing catch important defects before users hit them?
