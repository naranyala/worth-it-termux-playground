"""Tests for the file-organizer experiment.

Run from the experiment directory:

    python3 -m unittest discover -s tests -v

or simply:

    bash tests/run.sh

Every test works in a temporary directory and never touches real files.
"""

import os
import sys
import tempfile
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(TESTS_DIR)
sys.path.insert(0, os.path.join(EXPERIMENT_DIR, "src"))

import file_organizer  # noqa: E402


class FileOrganizerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.target = os.path.join(self.tmp.name, "downloads")
        os.makedirs(self.target)
        self.log = os.path.join(self.tmp.name, "state", "moves.log")
        # The tool refuses to work outside $HOME, so the temporary directory
        # is used as the home for the duration of the test.
        self._old_home = os.environ.get("HOME")
        os.environ["HOME"] = self.tmp.name

    def tearDown(self):
        if self._old_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = self._old_home
        self.tmp.cleanup()

    def make(self, name, content="x"):
        path = os.path.join(self.target, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def test_category_for_known_extensions(self):
        self.assertEqual(file_organizer.category_for("a.png"), "images")
        self.assertEqual(file_organizer.category_for("a.MP4"), "video")
        self.assertEqual(file_organizer.category_for("a.pdf"), "documents")
        self.assertEqual(file_organizer.category_for("a.zip"), "archives")
        self.assertEqual(file_organizer.category_for("a.py"), "code")

    def test_category_for_unknown_extension(self):
        self.assertEqual(file_organizer.category_for("a.qqq"), "other")
        self.assertEqual(file_organizer.category_for("noext"), "other")

    def test_is_inside(self):
        root = file_organizer.Path(self.target)
        self.assertTrue(file_organizer.is_inside(root, root))
        self.assertTrue(file_organizer.is_inside(root / "a" / "b", root))
        self.assertFalse(file_organizer.is_inside(file_organizer.Path("/etc"), root))

    def test_dry_run_moves_nothing(self):
        import contextlib
        import io

        self.make("photo.png")
        self.make("notes.txt")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = file_organizer.main([self.target, "--dry-run", "--log", self.log])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(os.path.join(self.target, "photo.png")))
        self.assertFalse(os.path.exists(os.path.join(self.target, "images")))
        self.assertFalse(os.path.exists(self.log))
        self.assertIn("dry run", out.getvalue())

    def test_apply_moves_files_and_logs(self):
        import contextlib
        import io

        self.make("photo.png")
        self.make("notes.txt")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = file_organizer.main([self.target, "--apply", "--log", self.log])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(os.path.join(self.target, "images", "photo.png")))
        self.assertTrue(os.path.exists(os.path.join(self.target, "documents", "notes.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.target, "photo.png")))
        self.assertTrue(os.path.exists(self.log))
        with open(self.log, encoding="utf-8") as handle:
            log_text = handle.read()
        self.assertIn("photo.png", log_text)

    def test_apply_is_idempotent(self):
        import contextlib
        import io

        self.make("photo.png")
        for _ in range(2):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = file_organizer.main([self.target, "--apply", "--log", self.log])
            self.assertEqual(code, 0)
        # The second run has nothing left to do.
        self.assertTrue(os.path.exists(os.path.join(self.target, "images", "photo.png")))

    def test_existing_destination_is_not_overwritten(self):
        import contextlib
        import io

        self.make("photo.png")
        os.makedirs(os.path.join(self.target, "images"))
        with open(os.path.join(self.target, "images", "photo.png"), "w", encoding="utf-8") as handle:
            handle.write("keep me")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = file_organizer.main([self.target, "--apply", "--log", self.log])
        self.assertEqual(code, 0)
        with open(os.path.join(self.target, "images", "photo.png"), encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "keep me")
        self.assertTrue(os.path.exists(os.path.join(self.target, "photo.png")))

    def test_apply_and_dry_run_conflict(self):
        import contextlib
        import io

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = file_organizer.main([self.target, "--apply", "--dry-run"])
        self.assertEqual(code, 2)

    def test_missing_target_is_an_error(self):
        import contextlib
        import io

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = file_organizer.main([os.path.join(self.tmp.name, "nope")])
        self.assertEqual(code, 2)
        self.assertIn("does not exist", err.getvalue())

    def test_refuses_target_outside_home(self):
        import contextlib
        import io

        # A directory that is not under the (temporary) home of this test.
        with tempfile.TemporaryDirectory() as elsewhere:
            outside = os.path.join(elsewhere, "outside")
            os.makedirs(outside)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = file_organizer.main([outside])
        self.assertEqual(code, 2)
        self.assertIn("refusing", err.getvalue())

    def test_refuses_system_path(self):
        import contextlib
        import io

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = file_organizer.main(["/etc"])
        self.assertEqual(code, 2)

    def test_undo_restores_files(self):
        import contextlib
        import io

        self.make("photo.png")
        with contextlib.redirect_stdout(io.StringIO()):
            file_organizer.main([self.target, "--apply", "--log", self.log])
        self.assertTrue(os.path.exists(os.path.join(self.target, "images", "photo.png")))

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = file_organizer.main([self.target, "--undo", "--log", self.log])
        self.assertEqual(code, 0)
        self.assertIn("would restore", out.getvalue())
        # Dry run: nothing moved back yet.
        self.assertTrue(os.path.exists(os.path.join(self.target, "images", "photo.png")))

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = file_organizer.main([self.target, "--undo", "--apply", "--log", self.log])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(os.path.join(self.target, "photo.png")))
        self.assertFalse(os.path.exists(os.path.join(self.target, "images", "photo.png")))

    def test_plan_moves_stays_inside_target(self):
        target = file_organizer.Path(self.target)
        outside = file_organizer.Path(self.tmp.name) / "outside.png"
        outside.write_text("x", encoding="utf-8")
        moves = file_organizer.plan_moves([outside], target)
        self.assertEqual(moves, [])

    def test_never_deletes_a_file(self):
        import contextlib
        import io

        self.make("photo.png")
        self.make("doc.pdf")
        with contextlib.redirect_stdout(io.StringIO()):
            file_organizer.main([self.target, "--apply", "--log", self.log])
        # Every file that was there before still exists somewhere under the
        # target: nothing was deleted, only moved.
        for name in ("photo.png", "doc.pdf"):
            found = False
            for dirpath, _dirnames, filenames in os.walk(self.target):
                if name in filenames:
                    found = True
                    break
            self.assertTrue(found, "file %s disappeared" % name)
        self.assertTrue(
            os.path.exists(os.path.join(self.target, "images", "photo.png"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.target, "documents", "doc.pdf"))
        )


if __name__ == "__main__":
    unittest.main()
