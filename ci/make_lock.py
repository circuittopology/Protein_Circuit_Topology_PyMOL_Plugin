"""
Generate a fully pinned conda lock file from ci/environment.yml.

    python ci/make_lock.py                     # solve, write ci/conda-lock-<platform>.txt
    python ci/make_lock.py --from-prefix PATH  # read an INSTALLED env instead; yields md5 checksums
    python ci/make_lock.py --check             # exit 1 if the committed lock does not match a solve

conda create --name proteinct --file ci/conda-lock-linux-64.txt

Two modes, because conda will not give checksums for a solve it has not performed:

  default        `conda create --dry-run --json`. Pins exact build strings, however conda 24.11's JSON
                 carries no hash field, so the lock is URL-only. Works without installing anything.
  --from-prefix  `conda list --explicit --md5` against a real environment. Checksum-bearing, and
                 what CI runs after building the environment (see .github/workflows/ci.yml).

Locks are per platform and can only be produced ON that platform, because conda solves for the host.
The file name records which platform it is for.
"""
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENVIRONMENT = REPO / "ci" / "environment.yml"
PROBE_ENV = "_ct_lock_probe"


def conda_exe() -> str:
    for name in ("mamba", "micromamba", "conda"):
        found = shutil.which(name)
        if found:
            return found
    msg = "no conda/mamba/micromamba on PATH"
    raise RuntimeError(msg)


def parse_environment() -> tuple[list[str], list[str]]:
    """Pull channels and dependency specs out of environment.yml (avoiding PyYAML)."""
    channels: list[str] = []
    specs: list[str] = []
    section = None
    for raw in ENVIRONMENT.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith((" ", "-")):
            section = line.split(":", 1)[0].strip()
            continue
        if line.lstrip().startswith("-"):
            value = line.lstrip()[1:].strip()
            if section == "channels":
                channels.append(value)
            elif section == "dependencies":
                specs.append(value)
    return channels, specs


def solve(channels: list[str], specs: list[str]) -> list[dict]:
    """Ask conda what it WOULD install."""
    cmd = [conda_exe(), "create", "--dry-run", "--json", "--name", PROBE_ENV]
    for channel in channels:
        cmd += ["-c", channel]
    cmd += specs

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(proc.stdout[-2000:] or proc.stderr[-2000:], file=sys.stderr)
        msg = f"conda solve failed with exit {proc.returncode}"
        raise RuntimeError(msg)

    text = proc.stdout[proc.stdout.index("{"):]
    payload = json.loads(text)
    if not payload.get("success"):
        msg = f"conda reported failure: {payload.get('message', payload)}"
        raise RuntimeError(msg)
    return payload["actions"]["LINK"]


def urls_from_solve(packages: list[dict]) -> list[str]:
    entries = []
    for pkg in packages:
        base = pkg["base_url"].rstrip("/")
        entries.append(f"{base}/{pkg['platform']}/{pkg['dist_name']}.conda")
    return entries


def from_prefix(prefix: str) -> list[str]:
    """Read an INSTALLED environment back out, with md5 checksums."""
    proc = subprocess.run(
        [conda_exe(), "list", "--explicit", "--md5", "--prefix", prefix],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        msg = f"conda list failed for {prefix}: {proc.stderr.strip()[-400:]}"
        raise RuntimeError(msg)
    return [
        line.strip() for line in proc.stdout.splitlines()
        if line.strip() and not line.startswith(("#", "@"))
    ]


def render(entries: list[str], subdir: str) -> str:
    lines = [
        "# Install with:",
        f"#     conda create --name proteinct --file ci/conda-lock-{subdir}.txt",
        "#",
        f"# platform: {subdir}",
        "@EXPLICIT",
    ]

    lines += sorted(entries)
    return "\n".join(lines) + "\n"


def target_platform() -> str:
    subdir = {"win32": "win-64", "darwin": "osx-64"}.get(sys.platform, "linux-64")
    if sys.platform == "darwin" and platform.machine() == "arm64":
        subdir = "osx-arm64"
    return subdir


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="compare the committed lock against a fresh solve")
    parser.add_argument("--from-prefix",
                        help="read installed environment instead of solving; yields md5 checksums")
    args = parser.parse_args(argv[1:])

    subdir = target_platform()
    target = REPO / "ci" / f"conda-lock-{subdir}.txt"

    if args.from_prefix:
        print(f"reading installed environment {args.from_prefix} for {subdir} ...")
        generated = render(from_prefix(args.from_prefix), subdir)
    else:
        channels, specs = parse_environment()
        print(f"solving {len(specs)} spec(s) from {ENVIRONMENT.name} for {subdir} ...")
        generated = render(urls_from_solve(solve(channels, specs)), subdir)

    if args.check:
        if not target.is_file():
            print(f"FAIL: {target.relative_to(REPO)} does not exist; run ci/make_lock.py")

            return 1
        if target.read_text(encoding="utf-8") != generated:
            print(f"FAIL: {target.relative_to(REPO)} does not match a fresh solve")

            return 1

        print(f"OK: {target.relative_to(REPO)} matches")

        return 0

    target.write_text(generated, encoding="utf-8", newline="\n")
    packages = sum(1 for line in generated.splitlines() if not line.startswith(("#", "@")))

    print(f"wrote {target.relative_to(REPO)} ({packages} pinned packages)")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
