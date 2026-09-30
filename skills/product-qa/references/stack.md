# Stack Hints

Concrete tools and commands for the stacks used most often. Check the project first (`pubspec.yaml`, `package.json`, CI config, existing test folders) and follow its conventions. These are defaults, not overrides.

## Flutter / Dart
**Run:** `flutter analyze` · `flutter test` · `flutter test --coverage` · `flutter test integration_test/` (needs a device or emulator, so usually flag as manual in a cloud sandbox).

**Layers:**
- Unit: pure Dart logic, formatters, money math, parsers, state notifiers, blocs and cubits (`bloc_test`), Riverpod providers (`ProviderContainer` with overrides).
- Widget/component: `testWidgets` + `pumpWidget`. Assert on what the user sees (`find.text`, `find.bySemanticsLabel`) rather than widget internals. Cover loading, error, empty and disabled states. Use `tester.tap` twice quickly to catch double-submit.
- Golden tests for visually critical components, only when the project already uses them, since they are brittle across platforms.
- Integration: `integration_test` for 2 to 5 critical journeys.
- Mocks: `mocktail` (or `mockito` if already used). Fake the repository or HTTP layer, not internal classes.

**Mobile-specific risks:** `setState` or `emit` after dispose (async gap) · missing `mounted` checks · `BuildContext` used across async gaps · lifecycle (`AppLifecycleState.paused` mid-request) · stale local cache (Hive, SharedPreferences, Drift) after an upgrade · platform channels (permissions, notifications) · text scaling overflows · ads (rewarded ad closed early, failed to load, reward granted twice).

## NestJS / TypeScript
**Run:** `npm test` / `npx jest` · `npx jest --coverage` · `npm run test:e2e` · `npx tsc --noEmit` · `npm run lint`.

**Layers:**
- Unit: services with mocked repositories via `Test.createTestingModule` and provider overrides. Test guards, pipes and DTO validation (`class-validator`) directly.
- Integration: a real Postgres (Testcontainers or a disposable Supabase/local DB) for repository queries, transactions and constraints. Mocks can't catch a missing unique index or a wrong transaction boundary.
- API/contract: `supertest` against `app.getHttpServer()`. Check status codes, response shape, auth (no token, wrong user's token, expired token), validation errors, and idempotency (same request twice).
- Webhooks: signature verification with valid, invalid and missing signatures; replay; duplicate delivery; out-of-order delivery.

**Risks:** missing `await` (unhandled rejection, response sent before write) · transactions not wrapping multi-step writes · exceptions swallowed into a 200 · DTOs whose `whitelist` doesn't strip unknown fields · N+1 queries · timezone (store UTC, display WAT).

## Supabase / PostgreSQL
- **RLS:** test as `anon`, as the owner, and as another authenticated user for each of select, insert, update and delete. A missing policy on one operation is a common leak. The service-role key bypasses RLS, so never ship it to the client.
- Constraints: unique indexes for idempotency keys and references, FK `on delete` behaviour, NOT NULL, check constraints on amounts (≥ 0).
- Money columns: `bigint` kobo or `numeric`, never `float`/`real`.
- Concurrency: `SELECT ... FOR UPDATE` or a conditional `UPDATE ... WHERE balance >= amount` for debits. Test with two parallel requests.
- Migrations: apply on a copy of realistic data; check the rollback path; old app version against the new schema.
- Edge functions and triggers: test that they're idempotent and that trigger failures surface.
- Tools: `supabase start` for local, `supabase db reset`, `pgTAP` for policy and function tests.

## BullMQ / Redis
- Jobs are delivered at least once, so handlers must be idempotent. Use a `jobId` to dedupe enqueue, and check state before side effects.
- Test: handler throws halfway then retries · `attempts`/`backoff` exhausted (goes to failed; is someone alerted?) · stalled job after worker crash · repeatable or cron job timezone and overlap · concurrency > 1 on the same entity.
- Test handlers as plain functions (unit) plus one integration test with a real Redis (Testcontainers or `redis-memory-server`).
- Observability: log `jobId` plus the domain reference, and track the failed-job count.

## Nigerian payments & fintech
- Providers: Paystack, Flutterwave, Monnify, Mono/Okra (account data). Use sandbox keys and test cards/accounts. Real bank behaviour (NIP delays, reversals) usually has to be a manual or exploratory item.
- Always verify transactions server-side via the provider's verify endpoint. Never trust the client callback alone.
- Amounts in kobo (×100). Test ₦0, ₦1 and the per-transaction or KYC tier limit exactly, plus fee inclusion or exclusion.
- Transfer states: `pending`, then `success`/`failed`/`reversed`. A reversal can arrive hours later.
- Account name enquiry mismatch; bank downtime; duplicate `reference`.
- Sensitive data: BVN, NIN and PINs must never appear in logs or analytics.

## Test data & determinism
Freeze time (`clock`/`fake_async` in Dart; `jest.useFakeTimers` or an injected clock in Node). Seed random generators. Keep each test's data isolated. Don't call real third-party APIs from unit or integration tests; contract-test the boundary instead.
