#!/usr/bin/env python3
"""Pull every retired /product/ and /product-category/ URL Google still reports for
elevateaudiology.com from Search Console (16 months), with clicks/impressions/position.

Read-only. Uses the Apex service account (same key + impersonation as
scripts/apex-google-verify.py in AIS-OS). Writes redirects/gsc-product-urls.csv.

    python3 redirects/pull-gsc-product-urls.py [--site sc-domain:elevateaudiology.com]
"""
import csv, datetime as dt, os, sys
sys.path.insert(0, os.path.expanduser("~/AI OS/AIS-OS/scripts"))
import importlib
ver = importlib.import_module("apex-google-verify")
from googleapiclient.discovery import build

site = sys.argv[sys.argv.index("--site") + 1] if "--site" in sys.argv else "sc-domain:elevateaudiology.com"
svc = build("searchconsole", "v1", credentials=ver.creds(ver.GSC_SCOPES))
end = dt.date.today() - dt.timedelta(days=3)
start = end - dt.timedelta(days=16 * 30)
rows, start_row = [], 0
while True:
    body = {
        "startDate": start.isoformat(), "endDate": end.isoformat(),
        "dimensions": ["page"], "rowLimit": 5000, "startRow": start_row,
        "dimensionFilterGroups": [{"filters": [
            {"dimension": "page", "operator": "includingRegex", "expression": "/product(-category)?/"}]}],
    }
    r = svc.searchanalytics().query(siteUrl=site, body=body).execute()
    got = r.get("rows", [])
    rows += got
    if len(got) < 5000:
        break
    start_row += 5000
out = os.path.join(os.path.dirname(__file__), "gsc-product-urls.csv")
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["url", "clicks", "impressions", "ctr", "position"])
    for r in sorted(rows, key=lambda r: -r["clicks"]):
        w.writerow([r["keys"][0], int(r["clicks"]), int(r["impressions"]), round(r["ctr"], 4), round(r["position"], 1)])
print(f"{len(rows)} URLs, {sum(int(r['clicks']) for r in rows)} clicks, "
      f"{sum(int(r['impressions']) for r in rows)} impressions -> {out}")
