#!/usr/bin/env python3
"""habit-tracker: a small, offline habit tracker backed by sqlite3.

Standard library only. The database lives in a single file under the
user's home directory unless HABIT_DB or --db says otherwise.

Design notes:
  * Every write goes through sqlite transactions, so an interrupted run
    (Ctrl-C) leaves a consistent database.
  * Completing the same habit twice on the same day is a no-op, which
    makes the command safe to run from a cron-like job.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sqlite3
import sys
from pathlib import Path

PROG = "habit"

DEFAULT_DB = Path.home() / ".local" / "share" / "habit-tracker" / "habits.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS habits (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS completions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id     INTEGER NOT NULL REFERENCES habits(id),
    day          TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    UNIQUE (habit_id, day)
);
"""


def default_db_path() -> Path:
    """Database location: --db wins, then HABIT_DB, then the default."""
    env = os.environ.get("HABIT_DB")
    if env:
        return Path(env).expanduser()
    return DEFAULT_DB


def open_db(path: Path) -> sqlite3.Connection:
    """Open (creating if needed) the database and make sure the schema exists."""
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def today() -> dt.date:
    return dt.date.today()


def parse_day(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        raise ValueError("day must be in YYYY-MM-DD format, got: %s" % value)


def add_habit(conn: sqlite3.Connection, name: str, when: dt.date | None = None) -> bool:
    """Create a habit. Returns True when it was created, False when it existed."""
    name = name.strip()
    if not name:
        raise ValueError("habit name cannot be empty")
    stamp = (when or today()).isoformat()
    try:
        with conn:
            conn.execute(
                "INSERT INTO habits (name, created_at) VALUES (?, ?)", (name, stamp)
            )
    except sqlite3.IntegrityError:
        return False
    return True


def complete_habit(
    conn: sqlite3.Connection, name: str, day: dt.date | None = None
) -> tuple[bool, bool]:
    """Mark a habit done for a day.

    Returns (found, newly_created). Completing twice on the same day
    returns (True, False) instead of inserting a duplicate row.
    """
    name = name.strip()
    if not name:
        raise ValueError("habit name cannot be empty")
    row = conn.execute(
        "SELECT id FROM habits WHERE name = ? COLLATE NOCASE", (name,)
    ).fetchone()
    if row is None:
        return (False, False)
    day_str = (day or today()).isoformat()
    try:
        with conn:
            conn.execute(
                "INSERT INTO completions (habit_id, day, completed_at) VALUES (?, ?, ?)",
                (row["id"], day_str, dt.datetime.now().isoformat(timespec="seconds")),
            )
    except sqlite3.IntegrityError:
        return (True, False)
    return (True, True)


def streak_for(conn: sqlite3.Connection, habit_id: int, day: dt.date) -> int:
    """Number of consecutive completed days ending today or yesterday."""
    rows = conn.execute(
        "SELECT day FROM completions WHERE habit_id = ? ORDER BY day DESC", (habit_id,)
    ).fetchall()
    days = {dt.date.fromisoformat(r["day"]) for r in rows}
    if not days:
        return 0
    cursor = day if day in days else day - dt.timedelta(days=1)
    if cursor not in days:
        return 0
    length = 0
    while cursor in days:
        length += 1
        cursor -= dt.timedelta(days=1)
    return length


def habit_rows(conn: sqlite3.Connection, day: dt.date | None = None):
    """All habits with completion state for the given day."""
    day = day or today()
    rows = conn.execute(
        """
        SELECT h.id, h.name, h.created_at,
               (SELECT COUNT(*) FROM completions c
                 WHERE c.habit_id = h.id) AS total,
               (SELECT COUNT(*) FROM completions c
                 WHERE c.habit_id = h.id AND c.day = ?) AS done_today,
               (SELECT MAX(c.day) FROM completions c
                 WHERE c.habit_id = h.id) AS last_day
          FROM habits h
         ORDER BY h.name COLLATE NOCASE
        """,
        (day.isoformat(),),
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["streak"] = streak_for(conn, row["id"], day)
        result.append(item)
    return result


def cmd_add(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    created = add_habit(conn, args.name)
    if created:
        print("added habit: %s" % args.name.strip())
        return 0
    print("habit already exists: %s" % args.name.strip())
    return 0


def cmd_complete(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    day = parse_day(args.day) if args.day else today()
    found, created = complete_habit(conn, args.name, day)
    if not found:
        print("no such habit: %s" % args.name.strip(), file=sys.stderr)
        return 1
    if created:
        print("completed: %s (%s)" % (args.name.strip(), day.isoformat()))
    else:
        print("already completed: %s (%s)" % (args.name.strip(), day.isoformat()))
    return 0


def cmd_list(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    day = parse_day(args.day) if args.day else today()
    rows = habit_rows(conn, day)
    if not rows:
        print("no habits yet. Add one with: %s add \"drink water\"" % PROG)
        return 0
    if args.brief:
        for row in rows:
            mark = "x" if row["done_today"] else " "
            print(
                "[%s] %-18s streak %2d  total %3d  last %s"
                % (
                    mark,
                    row["name"][:18],
                    row["streak"],
                    row["total"],
                    row["last_day"] or "-",
                )
            )
        return 0
    print("habits for %s" % day.isoformat())
    for row in rows:
        mark = "done" if row["done_today"] else "open"
        print(
            "  %-20s %-5s streak %2d  total %3d  last %s"
            % (
                row["name"],
                mark,
                row["streak"],
                row["total"],
                row["last_day"] or "-",
            )
        )
    done = sum(1 for r in rows if r["done_today"])
    print("%d/%d done today" % (done, len(rows)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Track daily habits offline in a local sqlite3 database.",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="path to the sqlite database (default: $HABIT_DB or ~/.local/share/habit-tracker/habits.db)",
    )
    parser.add_argument(
        "--brief",
        action="store_true",
        help="compact one-line-per-habit output for narrow screens",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    p_add = sub.add_parser("add", help="add a habit")
    p_add.add_argument("name", help="habit name")
    p_add.set_defaults(func=cmd_add)

    p_complete = sub.add_parser("complete", help="mark a habit done for a day")
    p_complete.add_argument("name", help="habit name")
    p_complete.add_argument(
        "--day", default=None, help="day to complete, YYYY-MM-DD (default: today)"
    )
    p_complete.set_defaults(func=cmd_complete)

    p_list = sub.add_parser("list", help="list habits")
    p_list.add_argument(
        "--day", default=None, help="day to inspect, YYYY-MM-DD (default: today)"
    )
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 2
    db_path = Path(args.db).expanduser() if args.db else default_db_path()
    try:
        conn = open_db(db_path)
    except (sqlite3.Error, OSError) as exc:
        print("habit: cannot open database %s: %s" % (db_path, exc), file=sys.stderr)
        return 1
    try:
        return args.func(conn, args)
    except ValueError as exc:
        print("habit: %s" % exc, file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("habit: interrupted", file=sys.stderr)
        return 130
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
