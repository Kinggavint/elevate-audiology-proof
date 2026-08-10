# Infra

## cloudfront-redirects.js

Source of truth for the CloudFront Function `elevate-audiology-redirects`
(distribution `E1DNI6M0NO4BBS`, viewer-request event).

The site was migrated off WordPress and the old URL structure still earns real
traffic, so legacy URLs are 301'd to the page that genuinely replaced them.
Redirecting to a loosely-related parent is treated by Google as a soft 404 —
the authority is lost anyway *and* the visitor is confused — so a redirect is
only added where the destination really covers the old topic.

`cloudfront-redirects.min.js` is the deployed build. CloudFront Functions are
capped at 10,240 bytes and the readable source is over it; the minifier only
strips comments and indentation, it does not change logic.

### Deploying

```bash
ETAG=$(aws cloudfront describe-function --name elevate-audiology-redirects \
         --stage DEVELOPMENT --query ETag --output text)

aws cloudfront update-function --name elevate-audiology-redirects \
  --if-match "$ETAG" \
  --function-config '{"Comment":"Elevate Audiology SEO redirects from old WordPress URLs","Runtime":"cloudfront-js-2.0"}' \
  --function-code fileb://infra/cloudfront-redirects.min.js

# ALWAYS test against DEVELOPMENT first — publish-function is what goes live
aws cloudfront test-function --name elevate-audiology-redirects \
  --if-match "$NEW_ETAG" --stage DEVELOPMENT --event-object fileb://event.json

aws cloudfront publish-function --name elevate-audiology-redirects \
  --if-match "$NEW_ETAG"
```

### Added 2026-08-10 (second batch)

Five legacy URLs Dr. Tarvin listed in her 23 June email, with the destinations she and
Apex had already agreed in that thread. They had been returning 404 for 48 days.

| Old URL | Destination |
|---|---|
| `/audiology-services/` | `/hearing-testing/` |
| `/products/` | `/hearing-aids/` |
| `/about-us/our-team/` | `/our-team/` |
| `/tinnitus-management/` | `/tinnitus/` |
| `/lenire-tinnitus/` | `/lenire/` |

Note the single-segment ones (`/products/`, `/tinnitus-management/`, `/lenire-tinnitus/`,
`/audiology-services/`) are matched by `manualMap`, which runs before the blog-slug rule,
so they resolve correctly rather than falling through to `/blog/<slug>/`.

### Deliberately NOT handled

`/product/` and `/product-category/` — 153 URLs carrying roughly 17% of the
site's organic clicks (1,255 clicks / 181,654 impressions over 16 months) —
still redirect to the homepage. That is a soft 404 and it is bleeding traffic,
but whether to rebuild the store, point it at a new accessories page, or retire
it cleanly with a 410 is a business decision for the client. Left unchanged
pending that answer rather than guessed at.

Also held, for the same reason:

| URL | Why |
|---|---|
| `/lowcountry-listening-lab/` | 129 clicks — more than any other dead URL. Purpose unknown. |
| `/sonic-innovations-hearing-aids/` | 7,528 impressions, and `/manufacturers/` never mentions Sonic — redirecting there would be a soft 404. |
| `/turn-around-your-hearing-experience/` | Campaign page? No obvious equivalent. |
| `/giftofhearing/` | Charity programme? |
| `/medicalmonitoring/` | Ototoxicity monitoring? No current page covers it. |

Left as clean 404s on purpose (infrastructure junk, no destination makes
sense): `/bitnami/index.html/`, `/cdn-cgi/l/email-protection/`, `/robots.txt/`,
`/offline/`, `/portal/`.
