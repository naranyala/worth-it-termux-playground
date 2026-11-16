# file-organizer

Sort a directory of files into subfolders by extension. The tool never deletes
anything, does nothing by default, and writes a log so a run can be reversed.

## Goal

Take a messy download folder and turn it into `images/`, `video/`, `audio/`,
`documents/`, `archives/`, `code/` and `other/`, without losing anything and
without finding out afterwards that you needed a file back where it was. The
exercise is in writing a tool whose default behaviour is safe: preview first,
move only when told, and record what happened.

## Skill taught

Designing a destructive-adjacent tool around three habits: dry run by default,
an explicit opt-in flag for the real work, and a log that makes the work
reversible. You also get practice with `pathlib`, with path containment checks
(`Path.relative_to`) that stop a tool from straying outside the directory it
was pointed at, and with writing output atomically through a temporary file.

## Time

30 minutes.

## Difficulty

Intermediate. The moving is easy; the safety rules are the interesting part.

## Setup

```sh
pkg update && pkg upgrade
pkg install python
```

The default target is `~/storage/downloads`, which only exists after shared
storage is enabled:

```sh
termux-setup-storage
```

Pick "Allow" in the Android dialog. Without it you can still point the tool at
any directory under your home directory.

Run the tests (they work in a temporary directory and touch nothing real):

```sh
cd playground/file-organizer
bash tests/run.sh
```

## Usage

```sh
# Preview the default target. Nothing is moved.
bin/file-organizer

# Preview a specific directory
bin/file-organizer "$HOME/storage/downloads" --dry-run

# Actually move the files
bin/file-organizer --apply

# Sort a directory you keep in your home directory
bin/file-organizer "$HOME/inbox" --apply

# Also sort files inside subdirectories
bin/file-organizer "$HOME/inbox" --recursive --apply

# See what the last run would undo
bin/file-organizer --undo

# Put the files back
bin/file-organizer --undo --apply
```

Every move is appended to a log file, one tab-separated line per file:

```text
2026-03-14T09:31:02.118293	/data/data/com.termux/files/home/storage/downloads/photo.png	/data/data/com.termux/files/home/storage/downloads/images/photo.png
```

Useful environment variables:

```sh
export FILE_ORGANIZER_TARGET="$HOME/storage/downloads"
export FILE_ORGANIZER_LOG="$HOME/.local/state/file-organizer/moves.log"
```

## Phone caveats

- **Shared storage permissions.** `termux-setup-storage` must be run once and
  approved from the Android dialog. Without it `~/storage` does not exist and
  the tool exits with a message saying so.
- **Shared storage is slow.** Moving many small files on `/storage/emulated/0`
  takes noticeably longer than in `$HOME`. Prefer a working directory under
  `$HOME` if you move a lot of files.
- **Screen width.** The preview prints one line per file. On a narrow screen,
  pipe it through `head -20` or run it in `tmux`.
- **Downloads folder conventions.** Some Android apps write `.nomedia` or
  partial files with a `.part` suffix. The tool sorts by extension, so those
  land in `other/`.
- **Background execution.** Not applicable: run this while looking at it.
  Moving files is fast, but a big folder still takes a while.

## Cleanup

The files stay where they were moved. To remove only the state:

```sh
rm -rf "$HOME/.local/state/file-organizer"
```

To move everything back to the top level of the target directory, use the undo
command:

```sh
bin/file-organizer --undo --apply
```

The category folders the tool created are left empty; remove them by hand if
you want a clean directory.

## Safety notes

- **Nothing is ever deleted.** Files are moved, never removed.
- **Dry run by default.** `--apply` is required to move anything. `--dry-run`
  is accepted as an explicit way to ask for the preview.
- **Existing files are not overwritten.** If a destination file with the same
  name exists, that file is left alone and the move is skipped.
- **The tool stays inside the target directory.** Every planned move is
  checked against the target before anything happens.
- **System paths are refused.** Pointing the tool at `/`, `/etc`, `/usr` or a
  similar location is rejected, as is any directory outside `$HOME` and
  shared storage.
- **No root, no privileged ports, no network.**
- **Reversible.** Every move is logged, and `--undo --apply` puts the files of
  the last run back.

## Sample output

Preview:

```console
$ bin/file-organizer
target: /data/data/com.termux/files/home/storage/downloads
planned moves: 4
  invoice.pdf -> documents/invoice.pdf
  notes.txt -> documents/notes.txt
  photo.jpg -> images/photo.jpg
  setup-x86_64.iso -> other/setup-x86_64.iso
dry run: nothing was moved. Re-run with --apply to do it.
```

Applying:

```console
$ bin/file-organizer --apply
target: /data/data/com.termux/files/home/storage/downloads
planned moves: 4
  invoice.pdf -> documents/invoice.pdf
  notes.txt -> documents/notes.txt
  photo.jpg -> images/photo.jpg
  setup-x86_64.iso -> other/setup-x86_64.iso
moved 4 file(s)
log: /data/data/com.termux/files/home/.local/state/file-organizer/moves.log
undo with: file-organizer --undo
```

Undoing, first as a preview:

```console
$ bin/file-organizer --undo
  would restore setup-x86_64.iso -> setup-x86_64.iso
  would restore photo.jpg -> photo.jpg
  would restore notes.txt -> notes.txt
  would restore invoice.pdf -> invoice.pdf
dry run: 4 file(s) would be restored. Re-run with --apply to do it.
```

Then for real:

```console
$ bin/file-organizer --undo --apply
undo: restored 4 file(s), skipped 0
```

## Layout

```text
README.md       purpose, setup, usage, limitations
bin/            executable commands
src/            implementation
tests/          checks and sample data
.env.example    names of configuration values, never secrets
```
