#!/usr/bin/env python3
"""Drift check for fast-moving upstream facts in the Termux Playground docs.

Two things are checked when the network is reachable:

1. The Pi coding agent CLI documentation must still document the flags the
   playground docs rely on (for example ``--print`` and ``--continue``).
2. The Termux ``nodejs`` package build script reports its version and whether
   npm is still bundled.

When there is no network access the script exits 0 with a clear "skipped"
message, so it is safe to run everywhere (including offline CI runners).

Usage:
    python3 scripts/check-upstream.py [--offline] [--timeout SECONDS]

Standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from typing import List, Optional, Sequence, Tuple

PI_CLI_DOC_URL = (
    "https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/cli.md"
)
TERMUX_NODEJS_BUILD_URL = (
    "https://raw.githubusercontent.com/termux/termux-packages/master/packages/nodejs/build.sh"
)

# CLI flags the Termux Playground docs assume exist.
EXPECTED_PI_FLAGS: Tuple[str, ...] = (
    "--print",
    "--mode",
    "--continue",
    "--resume",
    "--tools",
    "--exclude-tools",
    "--approve",
    "--offline",
    "--export",
    "--model",
    "--thinking",
)

TERMUX_PKG_VERSION_RE = re.compile(r"^TERMUX_PKG_VERSION=(?P<value>.+)$", re.MULTILINE)
NO_LONGER_BUNDLED_RE = re.compile(r"no longer bundled", re.IGNORECASE)

USER_AGENT = "worth-it-termux-playground-check-upstream/1.0"


def log(message: str) -> None:
    print(f"[check-upstream] {message}")


def fetch(url: str, timeout: float) -> Optional[str]:
    """Fetch a URL and return its text, or None when it cannot be reached."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        log(f"HTTP error {exc.code} for {url}")
        return None
    except urllib.error.URLError as exc:
        log(f"network unavailable for {url}: {exc.reason}")
        return None
    except (TimeoutError, OSError) as exc:
        log(f"network error for {url}: {exc}")
        return None

    return raw.decode("utf-8", errors="replace")


def check_pi_flags(text: str) -> List[str]:
    """Return the list of expected CLI flags that are missing from the docs."""
    missing = []
    for flag in EXPECTED_PI_FLAGS:
        if flag not in text:
            missing.append(flag)
    return missing


def report_nodejs_build(text: str) -> None:
    """Report the Termux nodejs package version and npm bundling status."""
    match = TERMUX_PKG_VERSION_RE.search(text)
    if match:
        log(f"Termux nodejs TERMUX_PKG_VERSION = {match.group('value').strip()}")
    else:
        log("Termux nodejs build.sh: TERMUX_PKG_VERSION not found (upstream layout may have changed)")

    if NO_LONGER_BUNDLED_RE.search(text):
        log("Termux nodejs: npm is NO LONGER BUNDLED (build.sh says 'no longer bundled')")
        log("  -> docs must tell users to install npm separately (pkg install npm)")
    else:
        log("Termux nodejs: npm still appears to be bundled")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check whether upstream Pi CLI flags and Termux nodejs facts have drifted.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip all network checks and exit 0.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Per-request network timeout in seconds (default: 10).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.offline:
        log("offline mode requested (--offline): all upstream checks skipped.")
        log("summary: skipped (offline)")
        return 0

    log("checking Pi CLI documentation ...")
    pi_text = fetch(PI_CLI_DOC_URL, args.timeout)

    if pi_text is None:
        log("could not fetch the Pi CLI docs; skipping upstream checks.")
        log("summary: skipped (no network access)")
        return 0

    missing = check_pi_flags(pi_text)
    if missing:
        for flag in missing:
            log(f"WARNING: expected Pi CLI flag is missing from cli.md: {flag}")
        log(f"summary: failed ({len(missing)} missing flag(s): {', '.join(missing)})")
        return 1

    log(f"all {len(EXPECTED_PI_FLAGS)} expected Pi CLI flags are still documented.")

    log("checking Termux nodejs package build script ...")
    nodejs_text = fetch(TERMUX_NODEJS_BUILD_URL, args.timeout)
    if nodejs_text is None:
        log("could not fetch the Termux nodejs build.sh; skipping that part.")
    else:
        report_nodejs_build(nodejs_text)

    log("summary: ok (no drift detected)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
