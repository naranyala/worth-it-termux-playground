# habit-tracker

A small offline habit tracker. Habits and completions live in one sqlite3 file
under your home directory; nothing is sent anywhere.

## Goal

Build a working habit tracker that you can actually keep using on a phone:
add a habit, tick it off for the day, and see a short list that fits on a narrow
screen. Everything runs locally, with no account and no network.

## Skill taught

Using sqlite3 from Python with a schema that protects itself. The database
enforces one row per habit per day (`UNIQUE (habit_id, day)`), so the tool is
idempotent: running "complete" twice in a row changes nothing the second time.
That property is what makes it safe to call from a scheduled job.

## Time

20 minutes.

## Difficulty

Beginner. Standard library only, one file of implementation, and the schema
does the bookkeeping for you.

## Setup

```sh
pkg update && pkg upgrade
pkg install python
```

No add-on application is required. Everything here works without Termux:API.

Run the tests once to confirm the environment:

```sh
cd playground/habit-tracker
bash tests/run.sh
```

## Usage

```sh
# Add a habit
bin/habit add "drink water"
bin/habit add "read 10 pages"

# Mark a habit done for today (repeat runs are harmless)
bin/habit complete "drink water"

# Mark a habit done for a specific day
bin/habit complete "read 10 pages" --day 2026-03-14

# List everything, with streaks
bin/habit list

# Compact output for a narrow terminal
bin/habit --brief list

# Use a different database file
bin/habit --db "$HOME/habits-scratch.db" add "stretch"
```

Useful environment variables:

```sh
export HABIT_DB="$HOME/.local/share/habit-tracker/habits.db"
```

## Phone caveats

- **Screen width.** The default `list` output wraps on a narrow terminal. Use
  `--brief` for one line per habit.
- **Typing.** Quote habit names: `bin/habit add "drink water"`.
- **Battery and background work.** This tool is a foreground command, not a
  service. If you schedule it with `termux-job-scheduler`, Android may delay or
  skip the run, and the delay is not something the script can fix.
- **Shared storage.** The database is deliberately kept in `~/.local/share/`,
  not in `~/storage`, because sqlite needs reliable locking and file
  permissions that shared storage does not always provide.
- **Typing `--help` takes a moment** on a phone keyboard. The same flags work:
  `bin/habit -h`.

## Cleanup

```sh
rm -rf "$HOME/.local/share/habit-tracker"
```

If you set `HABIT_DB` elsewhere, remove that file instead. Nothing else is
written outside your home directory.

## Safety notes

- No network access. The script never opens a socket.
- No deletions of anything you did not explicitly remove with `rm`.
- No root, no system paths, no privileged ports.
- Writes are wrapped in sqlite transactions, so an interrupted run (`Ctrl-C`)
  leaves the database consistent.
- The tool only ever writes inside the database file it is given.

## Sample output

```console
$ bin/habit add "drink water"
added habit: drink water

$ bin/habit add "drink water"
habit already exists: drink water

$ bin/habit complete "drink water"
completed: drink water (2026-03-14)

$ bin/habit complete "drink water"
already completed: drink water (2026-03-14)

$ bin/habit --brief list
[ ] drink water          streak  0  total   0  last -
[ ] read 10 pages        streak  0  total   0  last -

$ bin/habit list
habits for 2026-03-14
  drink water          done  streak  1  total   1  last 2026-03-14
  read 10 pages        open  streak  0  total   0  last -
1/2 done today
```

## Layout

```text
README.md       purpose, setup, usage, limitations
bin/            executable commands
src/            implementation
tests/          checks and sample data
.env.example    names of configuration values, never secrets
```
