#!/usr/bin/env python3
"""file-organizer: sort a directory by file extension into subfolders.

Standard library only.

Rules that matter:
  * Dry run by default. Nothing moves until --apply is passed.
  * Nothing is ever deleted. Files are moved, and collisions are skipped.
  * The script refuses to touch anything outside the target directory.
  * Every move is written to a log file so the operation can be reversed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import sys
from pathlib import Path

PROG = "file-organizer"

DEFAULT_TARGET = Path.home() / "storage" / "downloads"
DEFAULT_LOG = Path.home() / ".local" / "state" / "file-organizer" / "moves.log"

# Extension -> subfolder name. Extensions not listed land in "other".
CATEGORIES = {
    "images": {
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic", ".svg", ".tiff",
    },
    "video": {".mp4", ".mkv", ".mov", ".avi", ".webm", ".3gp", ".m4v"},
    "audio": {".mp3", ".m4a", ".ogg", ".opus", ".wav", ".flac", ".aac"},
    "documents": {".pdf", ".txt", ".md", ".docx", ".doc", ".odt", ".rtf", ".epub"},
    "archives": {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar", ".zst"},
    "code": {".py", ".sh", ".js", ".ts", ".json", ".html", ".css", ".toml", ".yaml",
             ".yml", ".c", ".h", ".cpp", ".java", ".go", ".rs"},
}

# Files the script never touches, whatever their extension.
SKIP_NAMES = {".gitkeep", ".keep"}

# System locations the tool refuses to touch at all, even if they are
# passed explicitly. The tool is meant for shared storage and $HOME.
PROTECTED_PREFIXES = (
    "/",
    "/bin",
    "/boot",
    "/dev",
    "/etc",
    "/lib",
    "/lib64",
    "/oem",
    "/proc",
    "/root",
    "/sbin",
    "/sys",
    "/system",
    "/usr",
    "/vendor",
)


def category_for(name: str) -> str:
    """Return the subfolder name for a file name."""
    suffix = Path(name).suffix.lower()
    for folder, extensions in CATEGORIES.items():
        if suffix in extensions:
            return folder
    return "other"


def default_target() -> Path:
    env = os.environ.get("FILE_ORGANIZER_TARGET")
    if env:
        return Path(env).expanduser()
    return DEFAULT_TARGET


def resolve_target(value: str | None) -> Path:
    """Resolve the target directory, expanding ~ and making it absolute."""
    if value:
        return Path(value).expanduser().resolve()
    return default_target().expanduser().resolve()


def is_inside(path: Path, root: Path) -> bool:
    """True when path is root itself or lives under it."""
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def is_protected(path: Path) -> bool:
    """True when the path is a system location the tool must not touch."""
    if path == Path("/"):
        return True
    for prefix in PROTECTED_PREFIXES:
        if prefix == "/":
            continue
        if is_inside(path, Path(prefix)):
            return True
    return False


def collect_files(target: Path, recursive: bool) -> list[Path]:
    """List the regular files to consider, skipping the category folders."""
    files: list[Path] = []
    skip_dirs = set(CATEGORIES.keys())
    if recursive:
        for dirpath, dirnames, filenames in os.walk(target):
            dirnames[:] = sorted(d for d in dirnames if d not in skip_dirs)
            for filename in sorted(filenames):
                files.append(Path(dirpath) / filename)
    else:
        for entry in sorted(target.iterdir()):
            if entry.is_file():
                files.append(entry)
    return [f for f in files if f.name not in SKIP_NAMES]


def plan_moves(files: list[Path], target: Path) -> list[tuple[Path, Path]]:
    """Build the (source, destination) pairs. Collisions are skipped."""
    moves: list[tuple[Path, Path]] = []
    for source in files:
        if not is_inside(source, target):
            # Defensive: never plan a move that leaves the target directory.
            continue
        if source.parent == target and source.suffix.lower() == ".log":
            continue
        folder = category_for(source.name)
        destination = target / folder / source.name
        if not is_inside(destination, target):
            continue
        if destination.exists():
            # Never overwrite an existing file.
            continue
        moves.append((source, destination))
    return moves


def write_log(path: Path, records: list[dict]) -> None:
    """Append move records to the log file, atomically."""
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().isoformat(timespec="microseconds")
    lines = []
    for record in records:
        lines.append("%s\t%s\t%s\n" % (stamp, record["from"], record["to"]))
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    fd, tmp_name = None, None
    try:
        import tempfile

        fd, tmp_name = tempfile.mkstemp(
            dir=str(path.parent), prefix=".moves-", suffix=".log.tmp"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(existing)
            handle.writelines(lines)
        os.replace(tmp_name, path)
        tmp_name = None
    finally:
        if tmp_name and os.path.exists(tmp_name):
            os.unlink(tmp_name)


def undo_last_run(log_path: Path, target: Path, apply: bool) -> int:
    """Move the files of the most recent logged run back to where they came from.

    Without apply=True this only prints what would be restored.
    """
    if not log_path.exists():
        print("file-organizer: no log file at %s" % log_path, file=sys.stderr)
        return 1
    records = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        records.append({"when": parts[0], "from": parts[1], "to": parts[2]})
    if not records:
        print("file-organizer: the log file is empty", file=sys.stderr)
        return 1
    last_run = records[-1]["when"]
    batch = [r for r in records if r["when"] == last_run]
    restored = 0
    skipped = 0
    for record in reversed(batch):
        source = Path(record["to"])
        destination = Path(record["from"])
        if not is_inside(source, target) or not is_inside(destination, target):
            skipped += 1
            continue
        if not source.exists():
            skipped += 1
            continue
        if destination.exists():
            skipped += 1
            continue
        if not apply:
            print("  would restore %s -> %s" % (source.name, destination.name))
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        restored += 1
    if not apply:
        print("dry run: %d file(s) would be restored. Re-run with --apply to do it." % len(batch))
        return 0
    print("undo: restored %d file(s), skipped %d" % (restored, skipped))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Sort files in a directory into subfolders by extension. "
            "Dry run by default; use --apply to move files."
        ),
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="directory to sort (default: ~/storage/downloads)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="actually move files; without this nothing is changed",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the planned moves and change nothing (the default)",
    )
    parser.add_argument(
        "--log",
        default=None,
        help="move log file (default: $FILE_ORGANIZER_LOG or ~/.local/state/file-organizer/moves.log)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="also sort files in subdirectories of the target",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help=(
            "restore the files of the last logged run; prints what would happen "
            "unless --apply is also given"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.apply and args.dry_run:
        print(
            "file-organizer: --apply and --dry-run contradict each other",
            file=sys.stderr,
        )
        return 2

    log_path = (
        Path(args.log).expanduser()
        if args.log
        else Path(
            os.environ.get("FILE_ORGANIZER_LOG", str(DEFAULT_LOG))
        ).expanduser()
    )

    try:
        target = resolve_target(args.target)
    except OSError as exc:
        print("file-organizer: %s" % exc, file=sys.stderr)
        return 2

    if not target.exists():
        print(
            "file-organizer: target directory does not exist: %s\n"
            "  Run termux-setup-storage to expose shared storage, or pass a path." % target,
            file=sys.stderr,
        )
        return 2
    if not target.is_dir():
        print("file-organizer: target is not a directory: %s" % target, file=sys.stderr)
        return 2

    # Refuse to work outside the user's own space.
    home = Path.home().resolve()
    shared_storage = Path("/storage/emulated/0")
    if is_protected(target):
        print(
            "file-organizer: refusing to operate on the system path %s.\n"
            "  This tool only works inside your home directory or shared storage." % target,
            file=sys.stderr,
        )
        return 2
    if not (is_inside(target, home) or is_inside(target, shared_storage)):
        print(
            "file-organizer: refusing to operate on %s.\n"
            "  This tool only works inside your home directory or shared storage." % target,
            file=sys.stderr,
        )
        return 2

    if args.undo:
        return undo_last_run(log_path, target, args.apply)

    try:
        files = collect_files(target, args.recursive)
    except OSError as exc:
        print("file-organizer: cannot read %s: %s" % (target, exc), file=sys.stderr)
        return 1

    moves = plan_moves(files, target)

    if not moves:
        print("file-organizer: nothing to sort in %s" % target)
        return 0

    print("target: %s" % target)
    print("planned moves: %d" % len(moves))
    for source, destination in moves:
        print("  %s -> %s" % (source.name, destination.parent.name + "/" + destination.name))

    if not args.apply:
        print("dry run: nothing was moved. Re-run with --apply to do it.")
        return 0

    moved: list[dict] = []
    failed = 0
    for source, destination in moves:
        if not is_inside(source, target) or not is_inside(destination, target):
            failed += 1
            continue
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            moved.append({"from": str(source), "to": str(destination)})
        except OSError as exc:
            print("file-organizer: could not move %s: %s" % (source, exc), file=sys.stderr)
            failed += 1

    try:
        write_log(log_path, moved)
    except OSError as exc:
        print("file-organizer: cannot write the log file %s: %s" % (log_path, exc), file=sys.stderr)
        return 1

    print("moved %d file(s)" % len(moved))
    if failed:
        print("failed to move %d file(s)" % failed)
    print("log: %s" % log_path)
    print("undo with: %s --undo" % PROG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
