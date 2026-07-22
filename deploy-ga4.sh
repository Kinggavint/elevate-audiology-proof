#!/bin/bash
# Deploy GA4 injection to elevateaudiology.com
# Run from inside the elevate-audiology-proof repo root.
# Requires AWS CLI configured with creds that can write to s3://elevate-audiology
# and invalidate CloudFront distribution E1DNI6M0NO4BBS.

set -euo pipefail

BUCKET="elevate-audiology"
REGION="us-east-2"
DISTRIBUTION_ID="E1DNI6M0NO4BBS"

echo "==> Verifying AWS identity"
aws sts get-caller-identity

echo ""
echo "==> Counting HTML files in proof repo"
HTML_COUNT=$(find . -name "*.html" -not -path "./.git/*" | wc -l | tr -d ' ')
echo "Found $HTML_COUNT HTML files to sync"

echo ""
echo "==> Syncing HTML files to s3://$BUCKET (region: $REGION)"
# Only HTML files; preserve correct content-type and short cache so future
# changes propagate quickly. CloudFront invalidation below handles current cache.
aws s3 sync . "s3://$BUCKET/" \
  --region "$REGION" \
  --exclude "*" \
  --include "*.html" \
  --exclude ".git/*" \
  --exclude ".claude/*" \
  --exclude "deploy-ga4.sh" \
  --content-type "text/html; charset=utf-8" \
  --cache-control "public, max-age=300, must-revalidate" \
  --no-progress

echo ""
echo "==> Creating CloudFront invalidation for HTML paths"
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id "$DISTRIBUTION_ID" \
  --paths "/*.html" "/" "/*/index.html" "/*/" "/*/*/index.html" "/*/*/" \
  --query 'Invalidation.Id' \
  --output text)

echo "Invalidation ID: $INVALIDATION_ID"
echo "Status: in progress (typically completes in 2-5 minutes)"

echo ""
echo "==> Done. Live site will reflect GA4 install once invalidation completes."
echo ""
echo "Verify with:"
echo "  curl -s https://elevateaudiology.com/ | grep -A2 'gtag/js?id=G-9R5LCWET23'"
