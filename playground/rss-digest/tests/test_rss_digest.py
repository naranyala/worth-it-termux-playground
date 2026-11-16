"""Tests for the rss-digest experiment.

Run from the experiment directory:

    python3 -m unittest discover -s tests -v

or simply:

    bash tests/run.sh

The tests never touch the network: they feed the parser sample XML directly
and use the built-in http.server on 127.0.0.1 for the fetch path.
"""

import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(TESTS_DIR)
sys.path.insert(0, os.path.join(EXPERIMENT_DIR, "src"))

import rss_digest  # noqa: E402

RSS_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Example Feed</title>
    <link>http://example.invalid/</link>
    <description>Sample</description>
    <item>
      <title>First post</title>
      <link>http://example.invalid/1</link>
      <pubDate>Mon, 04 Mar 2024 10:00:00 +0000</pubDate>
      <description>Body of the first post</description>
    </item>
    <item>
      <title>Second post</title>
      <link>http://example.invalid/2</link>
      <pubDate>Tue, 05 Mar 2024 10:00:00 +0000</pubDate>
      <description>Body of the second post</description>
    </item>
  </channel>
</rss>
"""

ATOM_SAMPLE = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Atom Example</title>
  <entry>
    <title>Atom entry</title>
    <link href="http://example.invalid/a1"/>
    <updated>2024-03-04T10:00:00Z</updated>
    <summary>Atom summary</summary>
  </entry>
</feed>
"""


class _Handler(BaseHTTPRequestHandler):
    body = RSS_SAMPLE.encode("utf-8")

    def do_GET(self):  # noqa: N802 - name fixed by BaseHTTPRequestHandler
        self.send_response(200)
        self.send_header("Content-Type", "application/rss+xml")
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *args):  # silence the test output
        return


class RssDigestTest(unittest.TestCase):
    def test_parse_rss_entries(self):
        entries = rss_digest.parse_feed(RSS_SAMPLE.encode("utf-8"), 10)
        self.assertEqual(len(entries), 2)
        titles = [entry["title"] for entry in entries]
        self.assertIn("First post", titles)
        self.assertIn("Second post", titles)
        self.assertEqual(entries[0]["published"], "2024-03-05")

    def test_parse_rss_respects_limit(self):
        entries = rss_digest.parse_feed(RSS_SAMPLE.encode("utf-8"), 1)
        self.assertEqual(len(entries), 1)

    def test_parse_atom_entries(self):
        entries = rss_digest.parse_feed(ATOM_SAMPLE.encode("utf-8"), 10)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["title"], "Atom entry")
        self.assertEqual(entries[0]["link"], "http://example.invalid/a1")

    def test_parse_invalid_xml_raises(self):
        import xml.etree.ElementTree as ET

        with self.assertRaises(ET.ParseError):
            rss_digest.parse_feed(b"<not-closed>", 10)

    def test_parse_feed_spec(self):
        self.assertEqual(
            rss_digest.parse_feed_spec("Example <http://x.invalid/feed>"),
            ("Example", "http://x.invalid/feed"),
        )
        self.assertEqual(
            rss_digest.parse_feed_spec("http://x.invalid/feed"),
            ("http://x.invalid/feed", "http://x.invalid/feed"),
        )

    def test_parse_feed_spec_rejects_garbage(self):
        with self.assertRaises(ValueError):
            rss_digest.parse_feed_spec("")

    def test_read_feed_file_skips_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "feeds.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("# a comment\n\nExample <http://x.invalid/feed>\n")
            feeds = rss_digest.read_feed_file(rss_digest.Path(path))
        self.assertEqual(feeds, [("Example", "http://x.invalid/feed")])

    def test_read_feed_file_missing(self):
        with self.assertRaises(FileNotFoundError):
            rss_digest.read_feed_file(rss_digest.Path("/nonexistent/feeds.txt"))

    def test_cache_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = rss_digest.Path(tmp) / "feeds.json"
            cache = {"u": {"name": "n", "fetched_at": "now", "entries": []}}
            rss_digest.save_cache(path, cache)
            self.assertTrue(path.exists())
            self.assertEqual(rss_digest.load_cache(path), cache)

    def test_load_cache_ignores_garbage(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = rss_digest.Path(tmp) / "feeds.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(rss_digest.load_cache(path), {})

    def test_write_atomic_leaves_no_temp_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = rss_digest.Path(tmp) / "digest.txt"
            rss_digest.write_atomic(path, "hello\n")
            self.assertEqual(path.read_text(encoding="utf-8"), "hello\n")
            leftovers = [n for n in os.listdir(tmp) if n != "digest.txt"]
            self.assertEqual(leftovers, [])

    def test_collect_fetches_over_local_http(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = "http://127.0.0.1:%d/feed" % server.server_address[1]
            cache = {}
            results = rss_digest.collect([("Local", url)], cache, 5, 5.0, False)
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(results[0]["error"], "")
        self.assertEqual(len(results[0]["entries"]), 2)
        self.assertIn(url, cache)

    def test_collect_offline_uses_cache_only(self):
        cache = {"http://x.invalid/f": {"entries": [{"title": "cached", "published": "", "summary": "", "link": ""}]}}
        results = rss_digest.collect(
            [("Cached", "http://x.invalid/f")], cache, 5, 5.0, True
        )
        self.assertEqual(results[0]["error"], "")
        self.assertTrue(results[0]["cached"])
        self.assertEqual(results[0]["entries"][0]["title"], "cached")

    def test_collect_offline_without_cache_reports_error(self):
        results = rss_digest.collect([("None", "http://x.invalid/f")], {}, 5, 5.0, True)
        self.assertIn("offline", results[0]["error"])

    def test_render_digest_contains_titles(self):
        results = [
            {
                "name": "Feed",
                "url": "http://x.invalid/",
                "error": "",
                "entries": [
                    {
                        "title": "A post",
                        "link": "http://x.invalid/1",
                        "published": "2024-03-04",
                        "summary": "text",
                    }
                ],
            }
        ]
        text = rss_digest.render_digest(results, rss_digest.dt.datetime(2024, 3, 4))
        self.assertIn("== Feed", text)
        self.assertIn("A post", text)
        self.assertIn("2024-03-04", text)

    def test_dry_run_writes_nothing(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "digest.txt")
            cache_path = os.path.join(tmp, "cache.json")
            argv = [
                "--dry-run",
                "--output",
                out_path,
                "--cache",
                cache_path,
                "--offline",
                "http://x.invalid/f",
            ]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(rss_digest.main(argv), 0)
            self.assertFalse(os.path.exists(out_path))
            self.assertFalse(os.path.exists(cache_path))

    def test_cli_without_feeds_fails(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            feed_file = os.path.join(tmp, "feeds.txt")
            with open(feed_file, "w", encoding="utf-8") as handle:
                handle.write("")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = rss_digest.main(["--feed-file", feed_file])
        self.assertEqual(code, 2)
        self.assertIn("no feeds", err.getvalue())

    def test_cli_rejects_bad_limit(self):
        import contextlib
        import io

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = rss_digest.main(["--limit", "0", "http://x.invalid/f"])
        self.assertEqual(code, 2)
        self.assertIn("limit", err.getvalue())


if __name__ == "__main__":
    unittest.main()
