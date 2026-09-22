#!/bin/bash
# Deploy elevateaudiology.com — GATED, not a blind sync.
#
# History: this used to be `aws s3 sync . s3://elevate-audiology --include
# "*.html"` with no diff check at all. That's how 22 pages of real,
# already-shipped SEO/AEO content silently rotted for weeks — an
# out-of-band agent kept publishing straight to S3 without ever committing
# back, and this script would have blind-overwritten every one of those
# pages with the stale repo copy the moment anyone ran it. See
# AIS-OS/context/projects/elevate-drift-2026-09-22/ for the full incident.
#
# Now: every file is checked against gated_deploy.py's per-file baseline
# (deploy-baseline.json) before it's touched. If live doesn't match what we
# last confirmed was there, that file is refused and named — not
# overwritten — and the run keeps going for everything else. A blind sync
# is no longer possible through this script.
#
# Run from inside the elevate-audiology-proof repo root.
# Requires AWS CLI configured with creds that can read/write
# s3://elevate-audiology and invalidate CloudFront E1DNI6M0NO4BBS.
#
# Usage:
#   ./deploy-ga4.sh --dry-run                       # see what would happen, touch nothing
#   ./deploy-ga4.sh                                  # real deploy (needs deploy-baseline.json)
#   ./deploy-ga4.sh --baseline-dir /path/to/snapshot  # first run only, or to add new files

set -euo pipefail

echo "==> Verifying AWS identity"
aws sts get-caller-identity

echo ""
echo "==> Running gated deploy"
exec python3 "$(dirname "$0")/gated_deploy.py" "$@"
