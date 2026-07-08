#!/usr/bin/env python3
"""Bharat Consumer Pulse — monthly macro refresh (backbone 3a, monthly cadence).

India's public series update monthly, not daily. This fetches CPI (MOSPI via
data.gov.in) and TRAI telecom-subscriber totals where an API key is present,
writes data/latest.json + a history snapshot. Degrades gracefully to the last
known values so the site never breaks.

Env: DATAGOV_API_KEY (free at data.gov.in). Without it, the pulse cards stay
in their 'pending first refresh' state — honest, not fabricated.
"""
import json, os, datetime, urllib.request
from pathlib import Path

KEY = os.environ.get("DATAGOV_API_KEY", "")
OUT = Path("data/latest.json")

def get(url):
    return json.loads(urllib.request.urlopen(url, timeout=30).read())

out = {"fetched_at": datetime.datetime.utcnow().isoformat() + "Z", "cpi": None, "telecom": None,
       "note": "CPI: MOSPI via data.gov.in. Telecom subs: TRAI. Monthly cadence."}

# Load previous so we never regress to null on a transient failure
if OUT.exists():
    try:
        prev = json.load(open(OUT))
        out["cpi"], out["telecom"] = prev.get("cpi"), prev.get("telecom")
    except Exception:
        pass

if KEY:
    # data.gov.in resource IDs vary; these are placeholders to wire once you
    # pick the exact CPI + TRAI resources on the portal. Structure is ready.
    try:
        # Example CPI resource pattern (replace RESOURCE_ID from data.gov.in):
        # d = get(f"https://api.data.gov.in/resource/RESOURCE_ID?api-key={KEY}&format=json&limit=1&sort[month]=desc")
        # out["cpi"] = {"value": float(d["records"][0]["index"]), "date": d["records"][0]["month"]}
        print("DATAGOV_API_KEY present — wire the exact CPI/TRAI resource IDs from data.gov.in (see comments).")
    except Exception as e:
        print("data.gov.in fetch failed, keeping previous:", e)
else:
    print("no DATAGOV_API_KEY — pulse stays in pending state (honest, not fabricated)")

os.makedirs("data/history", exist_ok=True)
json.dump(out, open(OUT, "w"), indent=2)
json.dump(out, open(f"data/history/{datetime.date.today()}.json", "w"), indent=2)
print("wrote data/latest.json")
