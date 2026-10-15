# TruthWire — Implementation Plan

**Version:** 1.1 (Updated with Worldwide Architecture, Pilot: NP, US, CA + Nepali Unicode Standards)  
**Date:** 2026-10-14  
**Product:** Country-first hybrid news aggregation and evidence-verification portal  
**Pilot countries:** Nepal (`NP`), United States (`US`), and Canada (`CA`) (Worldwide scalable architecture)  
**Primary interfaces:** Responsive web app + Progressive Web App (PWA)  
**Special Directives:** 
- Full Nepali language display for Nepal news with native Unicode UTF-8 storage and rendering.
- Preeti to Unicode converter integration (legacy font transliteration fallback).
- Perfect Devanagari typography with complex conjunct support (`क्ष`, `त्र`, `ज्ञ`, `श्री`, `र्य`).
- Routine of Nepal Banda (RONB) & official Nepali sources tracking with stringent evidence-based verification.

---

## 1. Executive Summary

TruthWire lets users select a country and read two distinct feeds:

1. **Latest Updates:** rapid, clearly attributed reports that may still be developing or unverified.
2. **Verified Feed:** stories whose *specific factual claims* meet documented evidence standards and have passed the required review workflow.

The goal is **transparent sourcing and responsible verification**, not a promise that all published news is free from error. Never represent an LLM-generated confidence value as the mathematical probability that a news item is true.

### V1 goals

- Let users choose Nepal, the US, or Canada, switch countries at any time, and filter by topic. Expandable worldwide.
- Collect permitted news metadata from an authorized source registry.
- Deduplicate reports into stories while preserving each publisher's original article.
- Display Latest Updates promptly with status and source attribution.
- Offer a separate Verified Feed governed by a documented claim-level verification policy.
- Display evidence, disagreements, reviewers, timestamps, and correction history.
- Give authorized admins tools for sources, review queues, overrides, and corrections.
- Support English and native Nepali UI; preserve original Nepali script with UTF-8.

---

## 2. Key Product Decisions

| Decision | V1 default | Reason |
|---|---|---|
| Publishing model | Hybrid | Speed without conflating publication with verification |
| Pilot countries | Nepal (`NP`), US (`US`), Canada (`CA`) | Multi-lingual, multi-region validation (Worldwide scalable DB) |
| Nepali Typography | Unicode UTF-8 + Preeti Converter | Native Devanagari ligature accuracy (`क्ष`, `त्र`, `ज्ञ`, `श्री`, `र्य`) |
| Source strategy | Licensed APIs, permitted RSS, official datasets, approved social integrations | Reduces legal and operational risk |
| Verification granularity | Individual factual claims | Multi-claim articles can mix true, false, and unknown claims |
| Verified promotion | Deterministic rules + accountable reviewer approval | AI assists but cannot independently certify consequential claims |
| Frontend | Next.js (TypeScript, Tailwind CSS, Lucide, Devanagari fonts) | Responsive web/PWA |
| API | Python FastAPI | Clear async APIs and data processing |
| Database | PostgreSQL / SQLite (zero-config dev fallback) | Relational provenance and audit records |

---

## 3. Directory Structure

```text
TruthWire/
├── apps/
│   ├── web/                    # Next.js 15/14, TypeScript, Tailwind CSS, Devanagari font setup
│   └── api/                    # FastAPI HTTP service
├── services/
│   ├── ingest/                 # RSS, API connectors, Preeti-to-Unicode converter
│   ├── story/                  # Country tagging, clustering
│   └── verification/           # Claims, evidence, checks
├── packages/
│   ├── schemas/                # Shared pydantic schemas / contracts
│   └── nepali-utils/           # Preeti-to-Unicode converter & Devanagari normalizer
├── infra/
│   ├── docker-compose.yml
│   └── migrations/
├── docs/
│   ├── editorial-policy.md
│   ├── verification-policy.md
│   └── implementation.md
├── .env.example
└── README.md
```
