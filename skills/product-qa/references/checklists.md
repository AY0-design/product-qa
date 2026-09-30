# QA Checklists

Use these to generate risks and scenarios. Don't paste them wholesale. Pick the items that actually apply to the feature and turn them into concrete scenarios.

## Contents
1. Risk dimensions
2. Input boundaries
3. User state
4. System state
5. Timing & concurrency
6. UX states
7. External dependencies
8. Data integrity trace
9. Security

---

## 1. Risk dimensions

| Dimension | Question |
|---|---|
| Impact | What happens if this fails? |
| Likelihood | How likely is failure? (new code, complex logic, external calls, concurrency make it higher) |
| Detectability | Would we notice quickly? Silent failures rank higher |
| Recoverability | Can the user or system recover without support? |
| Scope | How many users are affected? |
| Data sensitivity | Could private data leak? |
| Financial impact | Could money be lost, duplicated or misreported? |
| Security impact | Could access be compromised? |

Risk priority ≈ Impact × Likelihood × (poor) Detectability. Rate each as Low / Medium / High / Critical.

## 2. Input boundaries
Empty · null · missing fields · min · max · min−1 / max+1 · zero · negative · decimals · very large numbers · wrong type · malformed (email, phone, date, currency) · duplicates · leading/trailing whitespace · Unicode and emoji · RTL text · very long strings · injection-looking strings (`' OR 1=1`, `<script>`) · locale formats (`1,000.50` vs `1.000,50`).

## 3. User state
New · existing · returning · logged-out · suspended or banned · deleted · partially onboarded (e.g. KYC incomplete) · incomplete profile · expired session · insufficient permissions · multiple devices at once · free vs paid tier.

## 4. System state
Empty DB · existing data · stale data · missing related record · corrupted or legacy-shaped data · partial state from a previous failed run · concurrent modification · eventual consistency lag · stale cache · feature flag on vs off · mid-migration schema.

## 5. Timing & concurrency
Timeout · retry · slow response · duplicate request (double tap, client retry, webhook redelivery) · race between two writers · out-of-order events · expired token mid-flow · scheduled job at boundary (midnight, month end, timezone/DST, WAT vs UTC) · request interrupted halfway · job runs twice · job never runs.

## 6. UX states
For each screen or action check: loading · success · error · empty · disabled · partial completion · retry · offline · permission-denied.

Ask:
- Does the user know what happened?
- Does the UI reflect server truth, or only optimistic local state?
- Can the user trigger the action twice?
- Is there a clear recovery path?
- Is the error message understandable and actionable?
- Are irreversible actions clearly signalled?
- Is the state correct after refresh, app restart, back-navigation, or returning from background?

## 7. External dependencies
Third-party APIs · payment providers · auth providers · DB · queues · caches · push/email/SMS · object storage · analytics · search · LLM APIs.

For each, test: unavailable · timeout · malformed response · unexpected status code · rate-limited (429) · slow · partial response · duplicate response or webhook · success that the caller never hears about (response lost).

## 8. Data integrity trace
For every state-changing operation, trace it end to end and check consistency at each step:

```text
Input → Validation → Business logic → Persistence → Event / side effect → API response → UI state
```

Test: duplicate records · missing records · wrong relationships or foreign keys · partial writes (step 1 committed, step 2 failed) · failed writes surfaced as success · duplicate events · out-of-order events · stale reads · concurrent updates (lost update) · migration forward and backward compatibility · old app version against new schema.

## 9. Security

**Authentication:** invalid credentials · expired session · token reuse after logout · refresh-token rotation · password reset flow (token expiry, reuse) · lockout after repeated failures · session invalidated on password change.

**Authorization:** access another user's resource by changing an ID (IDOR) · privilege escalation · admin-only endpoints · role change takes effect immediately · RLS policies (Supabase) enforce ownership for select, insert, update and delete.

**Input:** SQL/NoSQL injection · XSS in stored content · path traversal · file upload abuse (type, size, polyglot) · oversized payloads · unexpected encodings.

**Data exposure:** responses don't include other users' data or internal fields (password hashes, internal IDs, provider secrets) · logs contain no tokens, PINs, BVN/NIN, full card numbers or secrets · error messages don't leak stack traces.

Don't run destructive security tests against production unless explicitly authorized.
