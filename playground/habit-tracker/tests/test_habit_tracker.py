"""Tests for the habit-tracker experiment.

Run from the experiment directory:

    python3 -m unittest discover -s tests -v

or simply:

    bash tests/run.sh
"""

import datetime as dt
import os
import sys
import tempfile
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(TESTS_DIR)
sys.path.insert(0, os.path.join(EXPERIMENT_DIR, "src"))

import habit_tracker  # noqa: E402


class HabitTrackerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "habits.db")
        self.conn = habit_tracker.open_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_add_is_idempotent(self):
        self.assertTrue(habit_tracker.add_habit(self.conn, "drink water"))
        self.assertFalse(habit_tracker.add_habit(self.conn, "drink water"))
        self.assertFalse(habit_tracker.add_habit(self.conn, "Drink Water"))
        rows = habit_tracker.habit_rows(self.conn)
        self.assertEqual(len(rows), 1)

    def test_add_rejects_empty_name(self):
        with self.assertRaises(ValueError):
            habit_tracker.add_habit(self.conn, "   ")

    def test_complete_twice_same_day_is_a_noop(self):
        habit_tracker.add_habit(self.conn, "read")
        day = dt.date(2024, 5, 1)
        found, created = habit_tracker.complete_habit(self.conn, "read", day)
        self.assertTrue(found)
        self.assertTrue(created)
        found, created = habit_tracker.complete_habit(self.conn, "read", day)
        self.assertTrue(found)
        self.assertFalse(created)

    def test_complete_unknown_habit(self):
        found, created = habit_tracker.complete_habit(self.conn, "nope")
        self.assertFalse(found)
        self.assertFalse(created)

    def test_streak_counts_consecutive_days(self):
        habit_tracker.add_habit(self.conn, "read")
        for day in (dt.date(2024, 5, 1), dt.date(2024, 5, 2), dt.date(2024, 5, 3)):
            habit_tracker.complete_habit(self.conn, "read", day)
        rows = habit_tracker.habit_rows(self.conn, dt.date(2024, 5, 3))
        self.assertEqual(rows[0]["streak"], 3)
        self.assertEqual(rows[0]["total"], 3)
        self.assertEqual(rows[0]["done_today"], 1)

    def test_streak_breaks_on_gap(self):
        habit_tracker.add_habit(self.conn, "read")
        habit_tracker.complete_habit(self.conn, "read", dt.date(2024, 5, 1))
        habit_tracker.complete_habit(self.conn, "read", dt.date(2024, 5, 3))
        rows = habit_tracker.habit_rows(self.conn, dt.date(2024, 5, 3))
        self.assertEqual(rows[0]["streak"], 1)

    def test_database_file_is_created_under_home_like_path(self):
        path = os.path.join(self.tmp.name, "nested", "deeper", "h.db")
        conn = habit_tracker.open_db(path)
        conn.close()
        self.assertTrue(os.path.exists(path))

    def test_parse_day_rejects_bad_format(self):
        with self.assertRaises(ValueError):
            habit_tracker.parse_day("01-05-2024")

    def test_cli_add_list_and_brief(self):
        import io
        import contextlib

        argv = ["--db", self.db_path, "add", "stretch"]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(habit_tracker.main(argv), 0)
        self.assertIn("added habit", out.getvalue())

        argv = ["--db", self.db_path, "--brief", "list"]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(habit_tracker.main(argv), 0)
        self.assertIn("stretch", out.getvalue())

    def test_cli_complete_unknown_returns_error(self):
        import io
        import contextlib

        argv = ["--db", self.db_path, "complete", "missing"]
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(habit_tracker.main(argv), 1)
        self.assertIn("no such habit", err.getvalue())

    def test_cli_without_command_shows_help(self):
        import io
        import contextlib

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(habit_tracker.main([]), 2)
        self.assertIn("usage", out.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
