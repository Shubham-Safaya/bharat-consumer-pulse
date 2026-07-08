# Bharat Consumer Pulse

Audience-planning and mobile-first identity mechanics, demonstrated on India's
public data with fully synthetic identities. The India twin of
[US Consumer Pulse](https://shubham-safaya.github.io/us-consumer-pulse/).

**Live:** https://shubham-safaya.github.io/bharat-consumer-pulse/

## What it is (and is not)

A **methodology demonstration**. Every persona figure is an aggregate public
statistic — labelled with its vintage (Census 2011, NCP projections, or NFHS
2019-21). The identity graph runs on a **100% synthetic population** keyed on
synthetic phone-hashes; no real individuals, no PII. Built DPDP-Act-aware by
design — see `dpdp.html`.

## Pages

- **Persona builder** — state/UT × segment lens (urban/rural/wealth-quintile/
  internet/literate), on Census 2011 + NCP projections + NFHS-5. Reach, index
  vs national, activation-spec shape keyed on synthetic phone-hash. ≥2 datasets.
- **Synthetic identity graph (mobile-first)** — my
  [identity-resolver](https://github.com/Shubham-Safaya/identity-resolution-engine)
  engine resolving 100K synthetic persons where **phone-hash is the primary key**
  (UPI/banking/messaging reality), graded against manufactured ground truth. The
  headline lesson is the mobile edition of identifier-frequency capping: shared
  family phone numbers are the dominant false-merge source.
- **Macro pulse** — CPI (MOSPI) + telecom subscribers (TRAI), monthly cadence
  with history.
- **DPDP consent architecture** — how the 2023 Act reshapes identity systems
  (consent managers as infrastructure, mobile-first keys, purpose limitation).

## Data sources (all public, vintage-labelled on-page)

- Census of India 2011 — population, urban/rural, literacy (censusindia.gov.in)
- National Commission on Population — Projections 2011-2036 (current-year est.)
- NFHS-5 (2019-21) — wealth quintiles, internet use (MoHFW/IIPS)
- MOSPI CPI (monthly) · TRAI subscriber reports (monthly) via data.gov.in

## Regenerate

```bash
# synthetic identity graph (needs identity-resolver locally)
python3 scripts/build_synthetic_graph.py --persons 100000

# macro pulse (needs DATAGOV_API_KEY; degrades gracefully without)
python3 scripts/refresh.py
```

Monthly refresh runs via GitHub Actions (`.github/workflows/refresh.yml`),
snapshot-and-history pattern, `workflow_dispatch` enabled for manual firing.

Part of the [Shubham Safaya](https://shubham-safaya.github.io/) portfolio.
