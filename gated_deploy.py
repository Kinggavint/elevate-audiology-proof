#!/usr/bin/env python3
"""
Gated deploy for elevateaudiology.com. Replaces the old blind `aws s3 sync`
in deploy-ga4.sh, which could not tell the difference between "nothing
changed" and "someone else wrote to this file since we last looked" — the
exact bug that let an out-of-band SEO agent silently overwrite (and get
overwritten by) 22 pages for weeks.

The rule: before touching any S3 object, fetch what is ACTUALLY there right
now and compare it to what we last confirmed was there (the "baseline").
If they match, it is safe to push our new content — nothing unknown has
happened to this file since we checked. If they don't match, something
wrote to this object that we don't know about. We refuse that one file,
name it, and move on to the rest rather than silently clobbering it.

Baseline is tracked per-file in deploy-baseline.json (sha256 of the last
content we confirmed was live, keyed by repo-relative path). Deliberately
NOT a single git ref/tag: a run can deploy some files and refuse others,
and each file's baseline has to advance independently of the others'
outcome, or a refused file in one run would make its unrelated siblings
falsely "refuse" on the next run too.

First run: deploy-baseline.json won't exist. You MUST pass --baseline-dir
pointing at a directory of raw file content that you have separately
verified matches what's live right now (e.g. a fresh audit snapshot).
Refusing to guess is the point — this tool will not assume live is safe
to overwrite just because nothing has checked it before.

We read live via S3 GetObject (through the aws CLI, no SDK dependency —
matches every other deploy script in this stack), not the public HTTPS
URL. Some paths (the 5 duplicate-URL redirects) are intercepted at the
CDN edge by the elevate-audiology-redirects CloudFront Function before
they ever reach S3, so curling the public URL for those tells you about
the edge redirect, not about the object this tool is actually about to
overwrite. GetObject is the only source of truth for "what is in the
bucket right now."
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BUCKET = "elevate-audiology"
REGION = "us-east-2"
DISTRIBUTION_ID = "E1DNI6M0NO4BBS"
BASELINE_FILE = "deploy-baseline.json"  # repo root, tracked in git (small, and a useful audit trail of what we believed was live at each deploy)
EXCLUDE_NAMES = {"gated_deploy.py", "deploy-ga4.sh"}
EXCLUDE_DIR_PARTS = {".git", ".claude", "infra"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def find_html_files(root: Path) -> list[str]:
    out = []
    for p in root.rglob("*.html"):
        rel = p.relative_to(root)
        if rel.name in EXCLUDE_NAMES:
            continue
        if EXCLUDE_DIR_PARTS & set(rel.parts):
            continue
        out.append(str(rel))
    return sorted(out)


def s3_get(key: str) -> bytes | None:
    with tempfile.NamedTemporaryFile() as tf:
        proc = subprocess.run(
            ["aws", "s3api", "get-object", "--bucket", BUCKET, "--key", key,
             "--region", REGION, tf.name],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            if "NoSuchKey" in proc.stderr or "404" in proc.stderr or "Not Found" in proc.stderr:
                return None
            raise RuntimeError(f"s3api get-object failed for {key}: {proc.stderr.strip()}")
        return Path(tf.name).read_bytes()


def s3_put(key: str, content: bytes) -> None:
    with tempfile.NamedTemporaryFile() as tf:
        Path(tf.name).write_bytes(content)
        proc = subprocess.run(
            ["aws", "s3api", "put-object", "--bucket", BUCKET, "--key", key,
             "--region", REGION, "--body", tf.name,
             "--content-type", "text/html; charset=utf-8",
             "--cache-control", "public, max-age=300, must-revalidate"],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"s3api put-object failed for {key}: {proc.stderr.strip()}")


def cloudfront_invalidate(paths: list[str]) -> str:
    ref = "gated-deploy-" + sha(json.dumps(sorted(paths)).encode())[:16]
    proc = subprocess.run(
        ["aws", "cloudfront", "create-invalidation",
         "--distribution-id", DISTRIBUTION_ID,
         "--paths", "/*",
         "--query", "Invalidation.Id", "--output", "text"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"cloudfront create-invalidation failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def load_baseline(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Show what would happen, touch nothing.")
    ap.add_argument(
        "--baseline-dir",
        type=Path,
        default=None,
        help="First-run only (or to add newly-discovered files): directory of pre-verified live "
             "content, mirroring repo paths, used for any file with no entry yet in "
             f"{BASELINE_FILE}.",
    )
    args = ap.parse_args()

    repo_root = Path(__file__).parent
    baseline_path = repo_root / BASELINE_FILE
    baseline = load_baseline(baseline_path)

    files = find_html_files(repo_root)
    print(f"Considering {len(files)} HTML files.\n")

    refused: list[tuple[str, str]] = []
    deployed: list[str] = []
    unchanged: list[str] = []
    new_baseline = dict(baseline)

    for rel in files:
        key = rel  # flat static site: repo path == S3 key
        local_new = (repo_root / rel).read_bytes()
        live = s3_get(key)
        live_sha = sha(live) if live is not None else None

        if rel in baseline:
            expected_sha = baseline[rel]
        elif args.baseline_dir is not None and (args.baseline_dir / rel).exists():
            expected_sha = sha((args.baseline_dir / rel).read_bytes())
        elif live is None:
            expected_sha = None  # genuinely new file, no baseline to check
        else:
            print(
                f"REFUSING TO RUN: '{rel}' has no baseline entry in {BASELINE_FILE} and no match "
                "in --baseline-dir, but something IS already live at that path. I will not assume "
                "it's safe to overwrite content I've never verified. Pass --baseline-dir with a "
                "pre-verified copy of this file, or resolve it manually first.",
                file=sys.stderr,
            )
            sys.exit(2)

        if expected_sha is not None and live_sha != expected_sha:
            refused.append((rel, "live does not match last-known baseline — unexpected write since last deploy"))
            continue

        if live_sha == sha(local_new):
            unchanged.append(rel)
            new_baseline[rel] = live_sha
            continue

        deployed.append(rel)
        if not args.dry_run:
            s3_put(key, local_new)
        new_baseline[rel] = sha(local_new)

    print(f"Unchanged (live already matches HEAD): {len(unchanged)}")
    print(f"Deployed: {len(deployed)}")
    for f in deployed:
        print(f"  -> {f}")
    if refused:
        print(f"\nREFUSED ({len(refused)}) — live has drifted since the last deploy, NOT touched:")
        for rel, reason in refused:
            print(f"  !! {rel}: {reason}")

    if args.dry_run:
        print("\n--dry-run: nothing was written to S3, no invalidation created, baseline file not updated.")
        return

    if deployed:
        inv_id = cloudfront_invalidate(deployed)
        print(f"\nCloudFront invalidation: {inv_id}")
    else:
        print("\nNothing deployed — skipping CloudFront invalidation.")

    # Baseline advances per-file regardless of other files' outcomes: a refusal on one
    # file must never block the next run from correctly recognizing an unrelated file
    # that deployed fine just now.
    baseline_path.write_text(json.dumps(new_baseline, indent=2, sort_keys=True) + "\n")
    print(f"\n{BASELINE_FILE} updated ({len(new_baseline)} files tracked).")

    if refused:
        print(f"\n{len(refused)} file(s) refused — look at those specific files before re-running.")
        sys.exit(1)


if __name__ == "__main__":
    main()
