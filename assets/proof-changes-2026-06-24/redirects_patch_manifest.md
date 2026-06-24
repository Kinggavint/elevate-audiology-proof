# Redirects Patch Manifest (to add to CloudFront Function)

Date: 2026-06-24

## Problem URLs (currently 404)
Verified 404 responses (CloudFront -> S3 NoSuchKey):
- https://elevateaudiology.com/audiology-services/
- https://elevateaudiology.com/products/
- https://elevateaudiology.com/about-us/our-team/
- https://elevateaudiology.com/tinnitus-management/
- https://elevateaudiology.com/lenire-tinnitus/

## Proposed redirect mappings
| From path | To path | Status |
|---|---|---|
| /audiology-services/ | /hearing-testing/ | 301 |
| /products/ | /hearing-aids/ | 301 |
| /about-us/our-team/ | /our-team/ | 301 |
| /tinnitus-management/ | /tinnitus/ | 301 |
| /lenire-tinnitus/ | /lenire/ | 301 |

## Evidence: destination pages exist (200)
- https://elevateaudiology.com/hearing-testing/
- https://elevateaudiology.com/hearing-aids/
- https://elevateaudiology.com/our-team/
- https://elevateaudiology.com/tinnitus/
- https://elevateaudiology.com/lenire/

## Next action required
We need cloudfront:GetFunction + cloudfront:UpdateFunction permission to patch the live CloudFront Function `elevate-audiology-redirects`.
