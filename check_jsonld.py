#!/usr/bin/env python3
"""Fail if any HTML page has an empty or unparseable JSON-LD block.

Why: the homepage shipped with three empty <script type="application/ld+json">
tags twice (2026-08-27, 2026-08-29, 2026-09-01). The repo copy was clean each
time; the bad copy came from an out-of-band publish straight to S3. Run this
before deploy (and from drift_check) so an empty block is named, not shipped.

Usage: python3 check_jsonld.py [dir]   -> exit 1 on any bad block
"""
import json, os, re, sys

RX = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S | re.I)

def main(root='.'):
    bad = 0
    for dp, _, fn in os.walk(root):
        if '/.git' in dp or 'node_modules' in dp:
            continue
        for f in fn:
            if not f.endswith('.html'):
                continue
            p = os.path.join(dp, f)
            for i, blk in enumerate(RX.findall(open(p, errors='ignore').read())):
                s = blk.strip()
                try:
                    if not s:
                        raise ValueError('empty block')
                    json.loads(s)
                except Exception as e:
                    bad += 1
                    print(f'BAD {p} block#{i}: {e}')
    print(f'{"FAIL" if bad else "OK"}: {bad} bad JSON-LD block(s)')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
