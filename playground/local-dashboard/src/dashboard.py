#!/usr/bin/env python3
"""local-dashboard: a tiny local status page served over loopback only.

Standard library only: http.server for the server, subprocess for the
Termux:API battery command, shutil for disk usage.

Safety:
  * The server binds to a loopback address only. Any other bind address is
    refused unless it is explicitly a loopback address.
  * The server serves a generated HTML page; it never reads or lists files
    from the filesystem.
  * Ctrl-C shuts the server down cleanly.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import shutil
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROG = "local-dashboard"

LOOPBACK_ADDRESSES = {"127.0.0.1", "::1", "localhost"}

PAGE_CSS = """
body { font-family: monospace; margin: 1rem; background: #111; color: #eee; }
h1 { font-size: 1.1rem; }
table { border-collapse: collapse; width: 100%; }
td, th { border: 1px solid #444; padding: 0.4rem 0.5rem; text-align: left;
         font-size: 0.9rem; vertical-align: top; }
th { background: #222; }
small { color: #999; }
"""


def is_loopback(host: str) -> bool:
    """True when the host is a loopback address."""
    if host in LOOPBACK_ADDRESSES:
        return True
    try:
        import ipaddress

        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def read_battery() -> dict:
    """Read the battery through Termux:API, if it is installed."""
    result = {"available": False, "detail": "Termux:API is not installed"}
    if not shutil.which("termux-battery-status"):
        result["detail"] = "Termux:API is not installed (pkg install termux-api)"
        return result
    try:
        output = subprocess.run(
            ["termux-battery-status"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        result["detail"] = "termux-battery-status failed: %s" % exc
        return result
    text = (output.stdout or "").strip()
    if not text:
        result["detail"] = "termux-battery-status returned nothing"
        return result
    result["available"] = True
    result["raw"] = text
    result["detail"] = text
    return result


def read_storage() -> dict:
    """Disk usage of the home directory."""
    usage = shutil.disk_usage(str(Path.home()))
    total = usage.total or 1
    used = usage.used
    free = usage.free
    return {
        "total": total,
        "used": used,
        "free": free,
        "percent": int(round(used * 100.0 / total)),
    }


def read_uptime(start: float) -> dict:
    """How long this server has been running, plus the system uptime if readable."""
    info = {"server_seconds": int(time.time() - start)}
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as handle:
            info["system_seconds"] = int(float(handle.read().split()[0]))
    except (OSError, ValueError, IndexError):
        info["system_seconds"] = None
    return info


def format_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0 or unit == "TB":
            return "%.1f %s" % (value, unit)
        value /= 1024.0
    return "%.1f TB" % value


def format_duration(seconds: int) -> str:
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return "%dh %dm %ds" % (hours, minutes, secs)
    if minutes:
        return "%dm %ds" % (minutes, secs)
    return "%ds" % secs


def render_page(start: float, host: str = "127.0.0.1") -> str:
    battery = read_battery()
    storage = read_storage()
    uptime = read_uptime(start)
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    rows.append(
        "<tr><th>Time</th><td>%s</td></tr>" % html.escape(now)
    )
    rows.append(
        "<tr><th>Battery</th><td><pre>%s</pre></td></tr>" % html.escape(battery["detail"])
    )
    rows.append(
        "<tr><th>Storage</th><td>%s used of %s (%d%%)<br>free: %s</td></tr>"
        % (
            format_bytes(storage["used"]),
            format_bytes(storage["total"]),
            storage["percent"],
            format_bytes(storage["free"]),
        )
    )
    rows.append(
        "<tr><th>Uptime</th><td>server: %s<br>system: %s</td></tr>"
        % (
            format_duration(uptime["server_seconds"]),
            format_duration(uptime["system_seconds"])
            if uptime.get("system_seconds") is not None
            else "not available",
        )
    )
    rows.append(
        "<tr><th>Home</th><td>%s</td></tr>" % html.escape(str(Path.home()))
    )

    return (
        "<!doctype html>\n"
        "<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>Termux dashboard</title>\n"
        "<style>%s</style></head><body>\n"
        "<h1>Termux dashboard</h1>\n"
        "<table>\n%s\n</table>\n"
        "<small>served on loopback only, %s</small>\n"
        "</body></html>\n"
        % (PAGE_CSS, "\n".join(rows), html.escape(host))
    )


class DashboardHandler(BaseHTTPRequestHandler):
    """Serves one generated page. No file listing, no directory access."""

    server_version = "local-dashboard/1.0"
    start_time = time.time()

    def do_GET(self):  # noqa: N802 - name fixed by BaseHTTPRequestHandler
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/":
            body = render_page(self.start_time).encode("utf-8")
            content_type = "text/html; charset=utf-8"
        elif path == "/health":
            body = b"ok\n"
            content_type = "text/plain; charset=utf-8"
        else:
            body = b"not found\n"
            content_type = "text/plain; charset=utf-8"
            self.send_response(404)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("local-dashboard: " + (fmt % args) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Serve a small battery/storage/uptime page on a loopback address. "
            "Non-loopback addresses are refused."
        ),
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("DASHBOARD_HOST", "127.0.0.1"),
        help="bind address; must be a loopback address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("DASHBOARD_PORT", "8080")),
        help="port to listen on (default: 8080)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="print the page to stdout and exit, without starting a server",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.port < 1024 or args.port > 65535:
        print(
            "local-dashboard: --port must be between 1024 and 65535, got %d"
            % args.port,
            file=sys.stderr,
        )
        return 2

    if not is_loopback(args.host):
        print(
            "local-dashboard: refusing to bind to %s.\n"
            "  This dashboard is loopback only. It has no authentication and\n"
            "  shows device information, so it must not be reachable from the\n"
            "  network. Use --host 127.0.0.1." % args.host,
            file=sys.stderr,
        )
        return 2

    if args.check:
        sys.stdout.write(render_page(time.time()))
        return 0

    try:
        server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    except OSError as exc:
        print(
            "local-dashboard: cannot bind to %s:%d: %s" % (args.host, args.port, exc),
            file=sys.stderr,
        )
        return 1

    print("local-dashboard: serving on http://%s:%d/" % (args.host, args.port))
    print("local-dashboard: press Ctrl-C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nlocal-dashboard: stopping")
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
