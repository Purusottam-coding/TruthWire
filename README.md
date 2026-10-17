# TruthWire (विश्वसनीय समाचार पोर्टल)

**Country-First Hybrid News Aggregation & Evidence-Verification Portal**  
*Pilot Countries: Nepal (`NP`), United States (`US`), Canada (`CA`) (Worldwide Scalable Architecture)*

---

## 🌟 Overview & Special Directives

TruthWire bridges the gap between fast-breaking developments and verified factual truth:
1. **Latest Updates (ताजा अपडेट):** Rapid, clearly attributed news reports from registered publishers, wires, and community networks (e.g. Routine of Nepal Banda - RONB), transparently labeled as `developing`.
2. **Verified Feed (प्रमाणित फिड):** Stories whose specific factual claims have been evaluated against primary official documents and verified newsrooms with documented reviewer decisions.

### 🇳🇵 Nepal News & Sourcing Architecture
- **Routine of Nepal Banda (RONB) & Community Wire Tracking:** Ingested with transparent attribution and classified as `community_wire`. Factual claims remain in `checking` / `unverified` status until corroborated by official gazettes (e.g., Nepal Rastra Bank, Civil Aviation Authority, Nepal Army) or accredited journalism.
- **Native Nepali Unicode UTF-8:** Complete database, API, and frontend text is stored in standard Devanagari Unicode (`U+0900` - `U+097F`).
- **Preeti to Unicode Converter:** Built-in conversion engine automatically transliterates legacy font encodings (Preeti) into normalized Unicode NFC.
- **Typographical Ligature Fidelity:** Native font styling configured with `Noto Sans Devanagari` and `Mukta` to guarantee accurate ligature rendering (`क्ष`, `त्र`, `ज्ञ`, `श्री`, `र्य` and all matras).

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+ & npm**

### 2. Backend (FastAPI) Setup

```powershell
cd d:\project\TruthWire\backend

# सजिलो तरिका:
npm run dev
```
*(वा सिधै पाइथनबाट: `..\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`)*

API Documentation: `http://127.0.0.1:8000/docs`

### 3. Frontend (Next.js) Setup

```powershell
cd d:\project\TruthWire\frontend

# Start Next.js development server
npm run dev
```
Web Application will be live at: `http://localhost:3000`

---

## 🛡️ Verification Workflow & Statuses

| Story State | Definition | Feed Placement |
|---|---|---|
| `developing` | Fast breaking story; source-attributed but uncorroborated | Latest Updates |
| `under_review` | Claim evaluation in progress by editorial desk | Latest Updates |
| `verified_summary` | Claims corroborated with primary source evidence | Verified Feed + Latest |
| `corrected` | Prior status updated following new evidence (audit logged) | Both Feeds |
| `retracted` | Claim disproven by conclusive evidence | Retraction Notice |

---

## 🧪 Preeti to Unicode Converter Utility

You can test the converter in both Python and TypeScript:

### Python:
```python
from packages.nepali_utils.converter import preeti_to_unicode

unicode_text = preeti_to_unicode("g]kfn cTolt ;'Gb/ b]z xf] .")
print(unicode_text)
# Output: नेपाल अत्यन्त सुन्दर देश हो ।
```

### TypeScript / Web:
The Web UI features an interactive **Preeti ➔ Unicode Normalizer** tab where journalists and editors can paste legacy text and receive instant UTF-8 Devanagari.
