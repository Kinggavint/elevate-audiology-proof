#!/usr/bin/env python3
"""Classify the retired store URLs (redirects/gsc-product-urls.csv) into the best LIVE page.

Writes redirects/store-map.csv: old_path, destination, confidence, rule, clicks, impressions, position.
Destinations are only pages that exist on the live site. Nothing here is deployed; see README.md.
"""
import csv, os, re
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "gsc-product-urls.csv")
OUT = os.path.join(HERE, "store-map.csv")

# (regex on the slug, destination, confidence, rule name) -- first match wins
RULES = [
    (r"batter", "/batteries/", "high", "battery"),
    (r"tinnitus|lenire|sound-generator|masker", "/tinnitus/", "high", "tinnitus"),
    (r"earplug|ear-plug|hearing-protection|musician|swim|noise-filter|sleep-plug", "/hearing-loss/", "low", "hearing-protection (no live protection page)"),
    (r"dome|ear-tip|eartip|open-ear-tip|tulip|power-dome|click-sleeve|sleeve|smokey", "/batteries/", "medium", "domes/tips -> accessories page (currently /batteries/)"),
    (r"wax|cerustop|cerushield|hf4|prowax|nanocare|guard|filter|cleaning|clean|brush|dryer|dehumidifier|dry|dessicant|wipes|drops|audgel|ear-gear|ear-planes|tube|tubing|earmold|retention|clip|sport-lock|cover|puffer|blower|loop|pick|stethoscope", "/batteries/", "medium", "supplies -> accessories page (currently /batteries/)"),
    (r"charger|charging|power-bank|case", "/batteries/", "medium", "charger/case -> accessories page (currently /batteries/)"),
    (r"receiver|speaker-unit|mini-rite|minirite|wire", "/repair/", "medium", "receiver/wire -> repair"),
    (r"oticon|phonak|resound|signia|starkey|unitron|widex|sonic|rexton|bernafon|philips", "/manufacturers/", "medium", "brand named, not an accessory -> manufacturers"),
    (r"hearing-aid|bte|ric|cic|itc|ite", "/hearing-aids/", "medium", "hearing aid"),
]

rows = []
with open(SRC) as f:
    for r in csv.DictReader(f):
        path = urlparse(r["url"]).path
        if not path.endswith("/"):
            path += "/"
        slug = path.strip("/").split("/", 1)[1] if "/" in path.strip("/") else ""
        dest, conf, rule = "/hearing-aids/", "low", "fallback (nothing on the live site covers it) -> 410 candidate"
        if path.startswith("/product-category/"):
            for rx, d, c, name in RULES:
                if re.search(rx, slug):
                    dest, conf, rule = d, c, "category: " + name
                    break
            else:
                dest, conf, rule = "/hearing-aids/", "low", "category fallback"
        else:
            for rx, d, c, name in RULES:
                if re.search(rx, slug):
                    dest, conf, rule = d, c, name
                    break
        rows.append({
            "old_path": path, "destination": dest, "confidence": conf, "rule": rule,
            "clicks": r["clicks"], "impressions": r["impressions"], "position": r["position"],
        })

rows.sort(key=lambda x: -int(x["clicks"]))
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

from collections import Counter
by_dest = Counter(); clicks = Counter(); by_conf = Counter()
for x in rows:
    by_dest[x["destination"]] += 1; clicks[x["destination"]] += int(x["clicks"]); by_conf[x["confidence"]] += 1
print(f"{len(rows)} URLs -> {OUT}")
for d, n in by_dest.most_common():
    print(f"  {d:<18} {n:>3} urls  {clicks[d]:>5} clicks")
print("confidence:", dict(by_conf))
