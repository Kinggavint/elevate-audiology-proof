# Retired store URL redirect map (PREP ONLY, pending Dr. Tarvin)

153 `/product/` and `/product-category/` URLs from the old WooCommerce store still 301 to the
homepage (a soft 404). Search Console, 16 months to 2026-10-05: **1,127 clicks / 155,544
impressions** on these URLs. Nothing in this folder is deployed; `infra/` is untouched.

| File | What |
|---|---|
| `pull-gsc-product-urls.py` | Read-only GSC pull (Apex service account). Refreshes `gsc-product-urls.csv`. |
| `gsc-product-urls.csv` | The 153 URLs with clicks / impressions / position. |
| `build-store-map.py` | Classifies each URL to the best LIVE page with a confidence column -> `store-map.csv`. |
| `store-map.csv` | The map. `low` = nothing on the live site covers it (410 candidate). |
| `render-cloudfront-map.py` | Renders the map into the repo's mechanism (CloudFront Function snippet + KeyValueStore import JSON). `--mode map|accessories|gone`. |
| `store-map.generated.js` / `store-map.kvs.json` | Rendered outputs for the current mode. Not referenced by `infra/`. |

**Constraint found:** the deployed function is 9,611 of the 10,240-byte CloudFront Function
cap, so a literal 153-entry map cannot be pasted into it. Either use the keyword snippet
(`store-map.generated.js`, ~1.2 KB) or move the lookup to a CloudFront KeyValueStore
(`store-map.kvs.json` is in `aws cloudfront-keyvaluestore` import format).

Wiring it in (after the decision): paste the snippet into `infra/cloudfront-redirects.js`
**before** the taxonomy block that sends `/product/` to `/`, re-minify, then follow
`infra/README.md` (DEVELOPMENT stage -> test-function -> publish).
