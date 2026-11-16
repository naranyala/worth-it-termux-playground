#!/usr/bin/env python3
"""rss-digest: fetch RSS/Atom feeds with urllib and render a plain-text digest.

Standard library only: urllib.request for fetching, xml.etree.ElementTree for
parsing, json for the on-disk cache.

Behaviour:
  * Feeds are configured in a simple text file (one URL per line, optional
    "Name <url>" form) or passed on the command line.
  * Every feed response is cached in a local JSON file so a second run with
    no network still produces a digest.
  * --dry-run prints the digest and writes nothing at all.
  * Writes go to a temporary file that is moved into place, so an interrupted
    run never leaves a half-written digest.
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import json
import os
import socket
import sys
import tempfile
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

PROG = "rss-digest"

DEFAULT_CACHE = Path.home() / ".cache" / "rss-digest" / "feeds.json"
DEFAULT_OUTPUT = Path.home() / ".local" / "share" / "rss-digest" / "digest.txt"
DEFAULT_FEEDS = Path.home() / ".config" / "rss-digest" / "feeds.txt"

USER_AGENT = "rss-digest/1.0 (Termux playground; stdlib urllib)"


def env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    if value:
        return Path(value).expanduser()
    return default


def parse_feed_spec(spec: str) -> tuple[str, str]:
    """Parse "Name <url>" or a bare URL into (name, url)."""
    spec = spec.strip()
    if not spec:
        raise ValueError("empty feed specification")
    if spec.endswith(">") and "<" in spec:
        start = spec.rfind("<")
        name = spec[:start].strip()
        url = spec[start + 1 : -1].strip()
        if not name or not url:
            raise ValueError("malformed feed specification: %s" % spec)
        return (name, url)
    return (spec, spec)


def read_feed_file(path: Path) -> list[tuple[str, str]]:
    """Read a feed list file. Blank lines and # comments are ignored."""
    if not path.exists():
        raise FileNotFoundError("feed file not found: %s" % path)
    feeds: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        feeds.append(parse_feed_spec(line))
    return feeds


def _text(node) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def parse_feed(data: bytes, limit: int) -> list[dict]:
    """Parse an RSS 2.0 or Atom document into a list of entry dicts.

    Each dict has: title, link, published (ISO date or ""), summary.
    """
    root = ET.fromstring(data)
    entries: list[dict] = []

    # Atom: <feed><entry>
    atom_entries = root.findall("{http://www.w3.org/2005/Atom}entry")
    if not atom_entries:
        atom_entries = root.findall("entry")
    for entry in atom_entries:
        title = _text(entry.find("title")) or _text(
            entry.find("{http://www.w3.org/2005/Atom}title")
        )
        link = ""
        link_node = entry.find("link")
        if link_node is None:
            link_node = entry.find("{http://www.w3.org/2005/Atom}link")
        if link_node is not None:
            link = (link_node.get("href") or "").strip()
        updated = _text(entry.find("updated")) or _text(
            entry.find("{http://www.w3.org/2005/Atom}updated")
        )
        summary = _text(entry.find("summary")) or _text(
            entry.find("{http://www.w3.org/2005/Atom}summary")
        )
        entries.append(
            {
                "title": title or "(untitled)",
                "link": link,
                "published": _normalise_date(updated),
                "summary": " ".join(summary.split()),
            }
        )

    # RSS 2.0: <rss><channel><item>
    if not entries:
        items = root.findall(".//item")
        for item in items:
            title = _text(item.find("title"))
            link = _text(item.find("link"))
            published = _text(item.find("pubDate")) or _text(item.find("date"))
            summary = _text(item.find("description"))
            entries.append(
                {
                    "title": title or "(untitled)",
                    "link": link,
                    "published": _normalise_date(published),
                    "summary": " ".join(summary.split()),
                }
            )

    entries.sort(key=lambda item: item["published"], reverse=True)
    return entries[:limit]


def _normalise_date(value: str) -> str:
    """Best-effort conversion of a feed date to YYYY-MM-DD, else ''."""
    value = (value or "").strip()
    if not value:
        return ""
    try:
        parsed = email.utils.parsedate_to_datetime(value)
        if parsed is not None:
            return parsed.date().isoformat()
    except (TypeError, ValueError):
        pass
    try:
        return dt.date.fromisoformat(value[:10]).isoformat()
    except ValueError:
        return value[:10] if len(value) >= 10 else ""


def fetch_feed(url: str, timeout: float) -> bytes:
    """Fetch a feed over http(s). Raises urllib.error.URLError on failure."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.5",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def load_cache(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_cache(path: Path, cache: dict) -> None:
    """Write the cache atomically: temp file, then mv."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=".feeds-", suffix=".json.tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(cache, handle, indent=1, sort_keys=True)
        os.replace(tmp_name, path)
    except BaseException:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


def write_atomic(path: Path, text: str) -> None:
    """Write a text file atomically: temp file, then mv."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=".digest-", suffix=".txt.tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except BaseException:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


def render_digest(
    results: list[dict], generated: dt.datetime, brief: bool = False
) -> str:
    """Render results into a plain-text digest."""
    lines = ["rss-digest", generated.strftime("%Y-%m-%d %H:%M"), ""]
    for result in results:
        lines.append("== %s" % result["name"])
        if result["error"]:
            lines.append("   ! %s" % result["error"])
        if not result["entries"]:
            lines.append("   (no entries)")
        for entry in result["entries"]:
            date = entry["published"] or "-"
            if brief:
                lines.append("   %s  %s" % (date, entry["title"]))
            else:
                lines.append("   %s  %s" % (date, entry["title"]))
                if entry["summary"]:
                    lines.append("       %s" % entry["summary"][:160])
                if entry["link"]:
                    lines.append("       %s" % entry["link"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def collect(
    feeds: list[tuple[str, str]],
    cache: dict,
    limit: int,
    timeout: float,
    offline: bool,
) -> list[dict]:
    """Fetch (or reuse the cache for) every feed and return per-feed results."""
    results: list[dict] = []
    for name, url in feeds:
        result = {"name": name, "url": url, "entries": [], "error": "", "cached": False}
        cached = cache.get(url)
        if offline:
            if cached:
                result["entries"] = cached.get("entries", [])[:limit]
                result["cached"] = True
            else:
                result["error"] = "offline and no cached copy of this feed"
            results.append(result)
            continue
        try:
            data = fetch_feed(url, timeout)
            entries = parse_feed(data, limit)
        except urllib.error.HTTPError as exc:
            result["error"] = "HTTP %s" % exc.code
            if cached:
                result["entries"] = cached.get("entries", [])[:limit]
                result["cached"] = True
        except urllib.error.URLError as exc:
            result["error"] = "network error: %s" % (exc.reason,)
            if cached:
                result["entries"] = cached.get("entries", [])[:limit]
                result["cached"] = True
        except socket.timeout:
            result["error"] = "timeout after %.0fs" % timeout
            if cached:
                result["entries"] = cached.get("entries", [])[:limit]
                result["cached"] = True
        except ET.ParseError as exc:
            result["error"] = "not valid XML: %s" % exc
        else:
            result["entries"] = entries
            cache[url] = {
                "name": name,
                "fetched_at": dt.datetime.now().isoformat(timespec="seconds"),
                "entries": entries,
            }
        results.append(result)
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Fetch RSS/Atom feeds and render a plain-text digest.",
    )
    parser.add_argument(
        "feeds",
        nargs="*",
        metavar="FEED",
        help="feed URL or \"Name <url>\"; overrides the feed file",
    )
    parser.add_argument(
        "--feed-file",
        default=None,
        help="file with one feed per line (default: $RSS_FEEDS_FILE or ~/.config/rss-digest/feeds.txt)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="digest file to write (default: $RSS_DIGEST_OUT or ~/.local/share/rss-digest/digest.txt)",
    )
    parser.add_argument(
        "--cache",
        default=None,
        help="cache file for downloaded feeds (default: $RSS_CACHE_FILE or ~/.cache/rss-digest/feeds.json)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="maximum entries per feed (default: 10)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="network timeout in seconds (default: 20)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="do not use the network; print the cached copy only",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the digest and write no files at all",
    )
    parser.add_argument(
        "--brief",
        action="store_true",
        help="titles only, for narrow screens",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.limit < 1:
        print("rss-digest: --limit must be at least 1", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("rss-digest: --timeout must be positive", file=sys.stderr)
        return 2

    feed_specs: list[tuple[str, str]] = []
    try:
        if args.feeds:
            for spec in args.feeds:
                feed_specs.append(parse_feed_spec(spec))
        else:
            feed_file = (
                Path(args.feed_file).expanduser()
                if args.feed_file
                else env_path("RSS_FEEDS_FILE", DEFAULT_FEEDS)
            )
            feed_specs = read_feed_file(feed_file)
    except (FileNotFoundError, ValueError) as exc:
        print("rss-digest: %s" % exc, file=sys.stderr)
        return 2

    if not feed_specs:
        print(
            "rss-digest: no feeds configured.\n"
            "Pass a URL, or create %s with one feed per line." % DEFAULT_FEEDS,
            file=sys.stderr,
        )
        return 2

    cache_path = (
        Path(args.cache).expanduser()
        if args.cache
        else env_path("RSS_CACHE_FILE", DEFAULT_CACHE)
    )
    output_path = (
        Path(args.output).expanduser()
        if args.output
        else env_path("RSS_DIGEST_OUT", DEFAULT_OUTPUT)
    )

    cache = load_cache(cache_path)
    try:
        results = collect(feed_specs, cache, args.limit, args.timeout, args.offline)
    except KeyboardInterrupt:
        print("rss-digest: interrupted", file=sys.stderr)
        return 130

    digest = render_digest(results, dt.datetime.now(), brief=args.brief)

    if args.dry_run:
        sys.stdout.write(digest)
        return 0

    try:
        save_cache(cache_path, cache)
        write_atomic(output_path, digest)
    except OSError as exc:
        print("rss-digest: cannot write files: %s" % exc, file=sys.stderr)
        return 1

    sys.stdout.write(digest)
    print("digest written to %s" % output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
