import urllib.request
import re

url = "https://www.hamropatro.com/"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TruthWire/1.0"})
with urllib.request.urlopen(req, timeout=5) as r:
    html = r.read().decode("utf-8", errors="ignore")

days = ["आइतबार", "सोमबार", "मंगलबार", "बुधबार", "बिहीबार", "शुक्रबार", "शनिबार"]
for d in days:
    idx = html.find(d)
    if idx != -1:
        snippet = html[max(0, idx-40):min(len(html), idx+80)]
        clean = " ".join(re.sub(r'<[^>]+>', ' ', snippet).split())
        print(f"Found {d}: {clean}")
