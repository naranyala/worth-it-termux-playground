"""Tests for the local-dashboard experiment.

Run from the experiment directory:

    python3 -m unittest discover -s tests -v

or simply:

    bash tests/run.sh

The tests start the server on 127.0.0.1 with an ephemeral port and talk to it
over loopback only.
"""

import os
import sys
import threading
import time
import unittest
import urllib.request

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(TESTS_DIR)
sys.path.insert(0, os.path.join(EXPERIMENT_DIR, "src"))

import dashboard  # noqa: E402


class LocalDashboardTest(unittest.TestCase):
    def test_is_loopback_recognises_loopback(self):
        self.assertTrue(dashboard.is_loopback("127.0.0.1"))
        self.assertTrue(dashboard.is_loopback("127.0.0.2"))
        self.assertTrue(dashboard.is_loopback("::1"))
        self.assertTrue(dashboard.is_loopback("localhost"))

    def test_is_loopback_rejects_routable_addresses(self):
        self.assertFalse(dashboard.is_loopback("0.0.0.0"))
        self.assertFalse(dashboard.is_loopback("192.168.1.10"))
        self.assertFalse(dashboard.is_loopback("example.com"))

    def test_non_loopback_host_is_refused(self):
        import contextlib
        import io

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = dashboard.main(["--host", "0.0.0.0", "--check"])
        self.assertEqual(code, 2)
        self.assertIn("refusing to bind", err.getvalue())

    def test_bad_port_is_refused(self):
        import contextlib
        import io

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = dashboard.main(["--port", "80"])
        self.assertEqual(code, 2)
        self.assertIn("port", err.getvalue())

    def test_check_prints_a_page(self):
        import contextlib
        import io

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = dashboard.main(["--check"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("Termux dashboard", text)
        self.assertIn("Storage", text)
        self.assertIn("Uptime", text)

    def test_format_bytes(self):
        self.assertEqual(dashboard.format_bytes(512), "512.0 B")
        self.assertTrue(dashboard.format_bytes(1024 * 1024).endswith("MB"))

    def test_format_duration(self):
        self.assertEqual(dashboard.format_duration(45), "45s")
        self.assertEqual(dashboard.format_duration(90), "1m 30s")
        self.assertEqual(dashboard.format_duration(3700), "1h 1m 40s")

    def test_read_storage_returns_numbers(self):
        storage = dashboard.read_storage()
        self.assertGreater(storage["total"], 0)
        self.assertTrue(0 <= storage["percent"] <= 100)

    def test_server_serves_the_page_on_loopback(self):
        from http.server import ThreadingHTTPServer

        server = ThreadingHTTPServer(("127.0.0.1", 0), dashboard.DashboardHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = "http://127.0.0.1:%d/" % server.server_address[1]
            with urllib.request.urlopen(url, timeout=10) as response:
                body = response.read().decode("utf-8")
                self.assertEqual(response.status, 200)
            self.assertIn("Termux dashboard", body)
            self.assertIn("Battery", body)

            health_url = "http://127.0.0.1:%d/health" % server.server_address[1]
            with urllib.request.urlopen(health_url, timeout=10) as response:
                self.assertEqual(response.read().decode("utf-8").strip(), "ok")
        finally:
            server.shutdown()
            server.server_close()

    def test_unknown_path_returns_404(self):
        from http.server import ThreadingHTTPServer
        import urllib.error

        server = ThreadingHTTPServer(("127.0.0.1", 0), dashboard.DashboardHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = "http://127.0.0.1:%d/nope" % server.server_address[1]
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(url, timeout=10)
            self.assertEqual(caught.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()

    def test_battery_reading_degrades_without_termux_api(self):
        battery = dashboard.read_battery()
        self.assertIn("available", battery)
        self.assertTrue(battery["detail"])


if __name__ == "__main__":
    unittest.main()
