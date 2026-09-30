# Domain Modes

Turn on every section that matches the product. A Flutter fintech app with an AI chat needs Mobile, API, Financial and AI.

## Contents
- Web application
- Mobile application
- API / backend
- Background jobs & queues
- AI product
- Financial product (mandatory whenever money moves)

---

## Web application
Browser compatibility (Chromium, Safari, Firefox) · responsive breakpoints · auth, sessions, cookies (SameSite, HttpOnly, Secure) · local and session storage · caching and stale bundles after deploy · accessibility (keyboard navigation, focus, labels, contrast) · network failure and slow 3G · multiple tabs doing the same action · back and forward buttons.

## Mobile application
- OS versions (min supported to latest) and device sizes including small screens and tablets
- Permissions: first ask, denied, "don't ask again", revoked in settings mid-session
- Lifecycle: background and foreground mid-request, app killed mid-flow, cold start from a push notification or deep link
- Interruptions: phone call, OS dialogs, keyboard covering inputs
- Offline, flaky network, network switch (Wi-Fi to mobile data) mid-request
- Low memory, low battery or power-saving mode, slow devices
- **App upgrades:** old cached data or schema with the new app, forced-update flow, old app version hitting the new API
- Store-specific: iOS vs Android back behaviour, notch and safe areas, text scaling or large fonts, dark mode

## API / backend
Request and response schema · status codes · authN and authZ per endpoint · validation errors are consistent and actionable · idempotency (idempotency key or natural key) · retry safety · timeouts · pagination (first, last and empty page, page-size limits, stable ordering) · rate limiting · backward compatibility for older clients · error response shape · no over-fetching of sensitive fields.

## Background jobs & queues
Job runs twice (at-least-once delivery) · job fails mid-way then retries · retry and backoff limits · dead-letter handling · poison messages · ordering assumptions · job scheduled while a previous run is still going · worker crash · visibility of job failures (alerts, not silent) · cron timezone.

## AI product
- Input variation: paraphrases, typos, mixed languages (e.g. English/Pidgin/Yoruba), very long or empty input
- Prompt injection via user content or retrieved documents
- Hallucination: fabricated facts, numbers or citations, especially in financial or health contexts
- Unsafe outputs and missing refusals; also over-refusal of legitimate requests
- Consistency across repeated runs, and behaviour after a model or version change
- Tool-calling: wrong tool, wrong arguments, acting on the wrong user's data
- Evaluation dataset plus regression benchmark kept in version control and run on every prompt or model change
- Latency and cost per request, and behaviour when the provider is rate-limited or down (graceful fallback)
- Grounding: when the AI summarizes user data (transactions, verses), check the numbers against the source data

## Financial product
Treat **duplicate execution as Critical** by default. Test:

- **Idempotency:** same request or idempotency key twice gives one transaction and the same response. Test double-tap, client retry after timeout, and webhook redelivery.
- **Response lost:** provider succeeded but our call timed out. The system must reconcile (verify via status endpoint) rather than retry blindly or mark it failed.
- **Balances:** debit and credit atomicity; no negative balance unless allowed; concurrent debits against the same wallet (lost update / double spend) need row locks or conditional updates.
- **Precision:** store money as integer minor units (kobo) or DECIMAL, never float. Check rounding rules, fee calculations and splits sum exactly to the total.
- **Currency:** NGN vs USD, conversion rate source and timestamp, display formatting (₦1,000.00).
- **Lifecycle:** pending, success, failed, reversed. Also refunds, partial refunds and chargebacks. Pending must resolve eventually.
- **Provider failure:** Paystack / Flutterwave / Monnify / bank downtime; NIBSS or NIP delays; wrong account name resolution.
- **Webhooks:** signature verification, replay, out-of-order delivery (success arriving before pending), duplicate delivery, and a webhook for an unknown reference.
- **Reconciliation:** internal ledger vs provider settlement report; a daily reconciliation job that flags mismatches.
- **Audit trail:** who, what, when and before/after for every money movement, immutable.
- **Authorization:** can't move money from another user's wallet by changing IDs; transaction PIN or OTP enforced and rate-limited.
- **Limits:** KYC tier limits, daily limits, minimum and maximum amounts, and the limit boundary exactly.
- **Parsing / categorisation (statements, expense tracking):** debit vs credit sign, dates in multiple formats, multi-page and multi-currency statements, duplicate imports of the same statement, and totals reconciling to the statement's closing balance.
