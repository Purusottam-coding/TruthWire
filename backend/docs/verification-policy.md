# TruthWire — Evidence Verification & Claim Assessment Policy (v1.0)

## 1. Core Principles

1. **Claim-Level Granularity**: Stories are not verified as wholesale blocks. Individual factual assertions are extracted, verified, and linked to evidence.
2. **Transparent Provenance**: Every verified claim must cite primary sources, official registers, or multiple independent corroborating outlets.
3. **Accountable Human Review**: Deterministic rules filter candidate claims, but human editorial review is required for promotion into the **Verified Feed**.
4. **Permanent Audit Trail**: All state transitions (e.g. `unverified` -> `corroborated` -> `disputed` -> `corrected`) are recorded in immutable logs with reviewer identity and timestamps.
5. **Freshness vs. Truth**: Rapid reports in the **Latest Updates** feed are labeled `developing` with transparent attribution; `developing` means unconfirmed, not false.

---

## 2. Claim Assessment Statuses

- `unverified`: Default state for newly ingested reports or social alerts.
- `checking`: Claim is actively being cross-referenced by reviewers or automated checking heuristics.
- `corroborated`: High-confidence factual match verified by at least one primary official source or two independent verified newsrooms.
- `disputed`: Conflicting reports exist from reputable sources; further evidence is needed.
- `refuted`: Documented evidence directly disproves the assertion.
- `inconclusive`: Insufficient verifiable evidence available within the verification window.

---

## 3. Routine of Nepal Banda (RONB) & Community Wire Rules

- Content from RONB and social community wires provides rapid situational alerts.
- **Rule**: Claims originating exclusively from social channels remain labeled `developing` / `unverified` in the **Latest Updates** feed until corroborated by:
  1. Official government bodies (e.g., Civil Aviation Authority of Nepal, Nepal Police, NRB, or ministries).
  2. Independent on-the-ground reporting from accredited journalists.
- When an RONB alert is corroborated, the evidence item must cite the official primary source alongside the community wire attribution.

---

## 4. Nepali Language and Unicode UTF-8 Typography Standards

1. **UTF-8 Native Encoding**: All Nepali content must be stored in standard Unicode UTF-8 (Devanagari Unicode block `U+0900` - `U+097F`).
2. **No Legacy Preeti**: Legacy font encodings (Preeti, Kantipur, etc.) are strictly prohibited from raw storage. Ingestion pipelines must automatically convert legacy text to Unicode NFC before database commit.
3. **Ligature & Conjunct Fidelity**: The presentation layer must guarantee proper rendering for complex conjuncts (`क्ष`, `त्र`, `ज्ञ`, `श्री`, `र्य`), halantas (`्`), and matras (`ि`, `ी`, `ु`, `ू`, `े`, `ै`, `ो`, `ौ`, `ं`, `ः`).
