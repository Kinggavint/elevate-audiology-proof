#!/usr/bin/env python3
"""
Daily drift check for elevateaudiology.com — Phase 4 of the 2026-09-22
reconciliation (see AIS-OS/context/projects/elevate-drift-2026-09-22/).

The root cause of that incident: the Apex SEO agent has S3 write access and
no git write access, so everything it publishes live rots the repo a little
further, silently, until someone happens to audit it. This script is the
catch: run it daily, and it can't silently rot for three weeks again — the
next divergence surfaces as a same-day PR instead.

What it does:
  1. For every *.html file, compare what's actually in S3 right now against
     what git HEAD on `main` has for that file.
  2. If nothing differs: log "no drift" and exit 0. This will be the
     overwhelming majority of days.
  3. If anything differs: create a branch off main, write S3's current
     content into each drifted file (mechanical backfill — exactly the
     bytes that are live, no cleverness), commit, push, and open a PR
     against main with `gh`. Exits 2 so the caller (a launchd job) knows
     to notify a human.

This NEVER merges anything itself and never touches main directly. A human
reviews the PR before it lands — same discipline as the 2026-09-22 fix,
where several of the "new" live sections turned out to carry real
content-fact changes (a patient testimonial, a softened FDA claim, a
statistic) that needed a human read, not just a mechanical diff.
"""
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

BUCKET = "elevate-audiology"
REGION = "us-east-2"
MAIN_BRANCH = "main"
EXCLUDE_NAMES = {"gated_deploy.py", "deploy-ga4.sh", "drift_check.py"}
EXCLUDE_DIR_PARTS = {".git", ".claude", "infra"}


def run(*args, cwd=None, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=check)


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
        proc = run("aws", "s3api", "get-object", "--bucket", BUCKET, "--key", key,
                   "--region", REGION, tf.name, check=False)
        if proc.returncode != 0:
            if "NoSuchKey" in proc.stderr or "404" in proc.stderr:
                return None
            raise RuntimeError(f"s3api get-object failed for {key}: {proc.stderr.strip()}")
        return Path(tf.name).read_bytes()


def git_show_head(repo: Path, path: str) -> bytes | None:
    proc = run("git", "show", f"{MAIN_BRANCH}:{path}", cwd=repo, check=False)
    if proc.returncode != 0:
        return None
    return proc.stdout.encode()


def main():
    # Defaults to the script's own location (fine for a manual/dev run), but
    # the launchd job MUST pass its own dedicated clone via --repo: this
    # script switches branches (`git checkout -B`), and running that against
    # Gavin's interactive working copy could yank the branch out from under
    # him mid-edit. A separate, automation-only clone means this can never
    # collide with anything he's doing by hand.
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
    # Always compare against main's committed state, regardless of what's
    # currently checked out — drift is a fact about main, not about whatever
    # branch happens to be active on this machine right now.
    run("git", "fetch", "origin", MAIN_BRANCH, cwd=repo)

    files = find_html_files(repo)
    print(f"Checking {len(files)} files against origin/{MAIN_BRANCH}...")

    drifted: list[str] = []
    for rel in files:
        live = s3_get(rel)
        head = git_show_head(repo, rel)
        # A file with no live object and nothing on HEAD either isn't drift,
        # it just doesn't exist yet on either side.
        if live is None and head is None:
            continue
        if live != head:
            drifted.append(rel)

    if not drifted:
        print("No drift. Live matches main exactly.")
        return 0

    print(f"DRIFT DETECTED in {len(drifted)} file(s):")
    for f in drifted:
        print(f"  {f}")

    branch = f"auto-drift-{date.today().isoformat()}"
    run("git", "checkout", "-B", branch, f"origin/{MAIN_BRANCH}", cwd=repo)

    for rel in drifted:
        live = s3_get(rel)
        dest = repo / rel
        if live is None:
            # Existed on main, gone from S3 now — leave the repo file alone,
            # this needs a human decision (deleted on purpose? mistake?),
            # not a silent auto-delete.
            print(f"  SKIPPING backfill for {rel}: exists on main but not in S3 anymore — needs a human look, not an auto-delete.")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(live)

    run("git", "add", "-A", cwd=repo)
    commit_msg = (
        f"chore: auto-detected drift backfill ({len(drifted)} file(s)), {date.today().isoformat()}\n\n"
        "Mechanical backfill from live S3 content — NOT hand-reviewed. Before "
        "merging, check for content-fact changes (medical claims, statistics, "
        "named testimonials, pricing, service claims), not just formatting — "
        "see the 2026-09-22 Elevate drift incident for exactly this failure "
        "mode. Files:\n" + "\n".join(f"- {f}" for f in drifted)
    )
    run("git", "commit", "-m", commit_msg, cwd=repo)
    run("git", "push", "-u", "origin", branch, cwd=repo)

    pr_body = (
        "Auto-detected: live S3 content differs from `main` for the file(s) below. "
        "This almost certainly means the SEO agent published directly again. "
        "Backfilled mechanically — **please read the diff for content-fact changes "
        "before merging**, not just SEO formatting.\n\n"
        + "\n".join(f"- `{f}`" for f in drifted)
    )
    pr = run("gh", "pr", "create", "--title", f"Auto-drift backfill: {len(drifted)} file(s), {date.today().isoformat()}",
              "--body", pr_body, "--base", MAIN_BRANCH, "--head", branch, cwd=repo, check=False)
    if pr.returncode == 0:
        print(f"\nPR opened: {pr.stdout.strip()}")
    else:
        print(f"\ngh pr create failed (branch {branch} is pushed regardless): {pr.stderr.strip()}", file=sys.stderr)

    return 2


if __name__ == "__main__":
    sys.exit(main())
