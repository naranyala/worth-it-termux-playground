#!/usr/bin/env python3
"""Check that every shell code block in the repository's Markdown files parses.

The script extracts fenced code blocks marked as shell (```sh, ```bash, ...) and
runs ``bash -n`` on each of them. A block that does not parse is reported with
its file and block index, and the script exits non-zero.

Blocks that are clearly illustrative fragments rather than runnable snippets
are skipped:

* the info string contains ``nocheck`` (e.g. ```` ```bash nocheck ````),
* the block contains an angle-bracket placeholder such as ``<path>``,
* the block contains a line consisting only of ``...``.

Usage:
    python3 scripts/check-snippets.py [--files GLOB] [--quiet]

Standard library only.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

# Fences we recognise: ``` or ~~~ (3 or more characters).
FENCE_RE = re.compile(r"^(?P<indent>\s*)(?P<fence>`{3,}|~{3,})\s*(?P<info>[^`]*)$")

# Info strings that mean "this is a shell snippet".
SHELL_LANGUAGES = {
    "sh",
    "bash",
    "shell",
    "zsh",
    "sh-session",
    "shell-session",
    "console",
}

# Info strings that mean "skip this block".
SKIP_HINT_RE = re.compile(r"\bnocheck\b", re.IGNORECASE)

# HTML-ish tags that must not be mistaken for a <placeholder>.
HTML_TAGS = {
    "a", "abbr", "b", "br", "code", "dd", "details", "div", "em", "h1", "h2",
    "h3", "h4", "h5", "h6", "hr", "i", "img", "kbd", "li", "ol", "p", "pre",
    "s", "small", "span", "strong", "sub", "summary", "sup", "table", "td",
    "th", "tr", "u", "ul",
}

# <something> where "something" is not a known HTML tag -> placeholder.
PLACEHOLDER_RE = re.compile(r"<\s*(?P<inner>[^<>\s]+)\s*>")

# A line consisting only of an ellipsis.
ELLIPSIS_LINE_RE = re.compile(r"^\s*\.\.\.\s*$")

DEFAULT_GLOBS = (
    "README.md",
    "docs/**/*.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "*.md",
)


@dataclass
class Block:
    """One fenced code block found in a Markdown file."""

    path: str
    index: int
    start_line: int
    info: str
    lines: List[str] = field(default_factory=list)


@dataclass
class Result:
    """Outcome of checking a single block."""

    block: Block
    status: str  # "ok" | "failed" | "skipped"
    detail: str = ""


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def iter_markdown_files(root: str, patterns: Sequence[str]) -> List[str]:
    """Expand the glob patterns into a sorted list of Markdown files."""
    found = set()
    for pattern in patterns:
        for path in glob.glob(os.path.join(root, pattern), recursive=True):
            if os.path.isfile(path) and path.endswith(".md"):
                found.add(os.path.abspath(path))
    return sorted(found)


def parse_blocks(path: str, text: str) -> List[Block]:
    """Extract fenced code blocks from a Markdown document."""
    lines = text.splitlines()
    blocks: List[Block] = []
    open_fence = None  # tuple of (fence_char, fence_len, info, start_line)
    current: List[str] = []
    counter = 0

    for number, line in enumerate(lines, start=1):
        if open_fence is None:
            match = FENCE_RE.match(line)
            if not match:
                continue
            fence = match.group("fence")
            open_fence = (fence[0], len(fence), match.group("info").strip(), number)
            current = []
            continue

        fence_char, fence_len, info, start_line = open_fence
        stripped = line.strip()
        # A closing fence uses the same char and is at least as long.
        if stripped.startswith(fence_char * fence_len) and set(stripped) == {fence_char}:
            if info:
                counter += 1
                blocks.append(
                    Block(
                        path=path,
                        index=counter,
                        start_line=start_line,
                        info=info,
                        lines=current,
                    )
                )
            open_fence = None
            current = []
            continue

        current.append(line)

    return blocks


def is_shell_block(block: Block) -> bool:
    """True when the info string marks the block as shell code."""
    info = block.info.strip().lower()
    if not info:
        return False
    first = info.split()[0]
    return first in SHELL_LANGUAGES


def has_placeholder(block: Block) -> bool:
    """True when the block contains obvious placeholder syntax."""
    for line in block.lines:
        if ELLIPSIS_LINE_RE.match(line):
            return True
        for match in PLACEHOLDER_RE.finditer(line):
            inner = match.group("inner").strip()
            if not inner:
                continue
            # Closing tags such as </h1> are markup, not placeholders.
            if inner.startswith("/"):
                continue
            if inner.lower() in HTML_TAGS:
                continue
            # Things like <your-api-key>, <path/to/file>, <...>
            return True
    return False


def should_skip(block: Block) -> str:
    """Return a reason to skip the block, or an empty string to check it."""
    if SKIP_HINT_RE.search(block.info):
        return "info string contains 'nocheck'"
    if has_placeholder(block):
        return "contains placeholder syntax"
    return ""


def check_block(block: Block) -> Result:
    """Run ``bash -n`` over the block."""
    reason = should_skip(block)
    if reason:
        return Result(block=block, status="skipped", detail=reason)

    script = "\n".join(block.lines)
    if script.strip() == "":
        return Result(block=block, status="skipped", detail="empty block")

    try:
        proc = subprocess.run(
            ["bash", "-n"],
            input=script,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError:
        return Result(block=block, status="skipped", detail="bash not available")

    if proc.returncode == 0:
        return Result(block=block, status="ok")

    detail = proc.stdout.strip() or "bash -n reported a syntax error"
    return Result(block=block, status="failed", detail=detail)


def relative(path: str, root: str) -> str:
    try:
        return os.path.relpath(path, root)
    except ValueError:  # pragma: no cover - different drives on Windows
        return path


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify that every shell snippet in the Markdown docs parses with 'bash -n'.",
    )
    parser.add_argument(
        "--files",
        action="append",
        metavar="GLOB",
        help=(
            "Glob of Markdown files to check (repeatable). "
            "Default: " + ", ".join(DEFAULT_GLOBS)
        ),
    )
    parser.add_argument(
        "--root",
        default=repo_root(),
        help="Repository root (default: the parent of this script's directory).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print failures and the final summary.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = os.path.abspath(args.root)
    patterns = tuple(args.files) if args.files else DEFAULT_GLOBS

    files = iter_markdown_files(root, patterns)
    if not files:
        print("check-snippets: no Markdown files matched; nothing to do.")
        print("summary: 0 file(s), 0 block(s), 0 failure(s)")
        return 0

    results: List[Result] = []
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except (OSError, UnicodeDecodeError) as exc:
            print(f"check-snippets: could not read {relative(path, root)}: {exc}", file=sys.stderr)
            continue

        for block in parse_blocks(path, text):
            if not is_shell_block(block):
                continue
            results.append(check_block(block))

    failures = [r for r in results if r.status == "failed"]
    skipped = [r for r in results if r.status == "skipped"]
    checked = [r for r in results if r.status == "ok"]

    if not args.quiet:
        for result in checked:
            print(
                f"ok      {relative(result.block.path, root)}"
                f" block #{result.block.index} (line {result.block.start_line})"
            )
        for result in skipped:
            print(
                f"skipped {relative(result.block.path, root)}"
                f" block #{result.block.index} (line {result.block.start_line}): {result.detail}"
            )

    for result in failures:
        print(
            f"FAIL    {relative(result.block.path, root)}"
            f" block #{result.block.index} (line {result.block.start_line}): {result.detail}",
            file=sys.stderr,
        )

    print(
        f"summary: {len(files)} file(s), {len(results)} shell block(s), "
        f"{len(checked)} ok, {len(skipped)} skipped, {len(failures)} failure(s)"
    )

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
