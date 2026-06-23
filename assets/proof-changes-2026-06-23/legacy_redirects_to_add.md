# Legacy redirects to add (requested by Dr. Tarvin) — 2026-06-23

These legacy URLs currently return 404.

Target behavior: HTTP 301 redirect to the new URL.

| Legacy URL | Target URL |
|---|---|
| /audiology-services/ | /hearing-testing/ |
| /products/ | /hearing-aids/ |
| /about-us/our-team/ | /our-team/ |
| /tinnitus-management/ | /tinnitus/ |
| /lenire-tinnitus/ | /lenire/ |

Verification commands

```bash
curl -sI https://elevateaudiology.com/audiology-services/ | sed -n '1,8p'
curl -sI https://elevateaudiology.com/products/ | sed -n '1,8p'
curl -sI https://elevateaudiology.com/about-us/our-team/ | sed -n '1,8p'
curl -sI https://elevateaudiology.com/tinnitus-management/ | sed -n '1,8p'
curl -sI https://elevateaudiology.com/lenire-tinnitus/ | sed -n '1,8p'
```
