# battery-notify

Send a phone notification when the battery drops to a threshold, using
Termux:API. The script is safe to run repeatedly: it stays quiet while the
battery is at the same low level.

## Goal

Build the smallest useful Android integration that still behaves: read a
hardware value through Termux:API, decide something with it, and act on the
phone. You also get a concrete example of a script that degrades gracefully
when an add-on application is missing.

## Skill taught

Writing a shell script against Termux:API that degrades instead of failing.
The script checks for `termux-battery-status` and `termux-notification` with
`command -v`, explains what to install when they are missing, and exits 0 so a
scheduled job does not fill the log with errors. It also keeps a small state
file so repeated runs do not spam the notification shade.

## Time

20 minutes.

## Difficulty

Beginner. About 150 lines of POSIX sh, no dependencies beyond coreutils.

## Setup

Install the Termux:API add-on application and its package. The add-on app
must come from the same source as Termux (F-Droid or the official GitHub
releases), or the two will not talk to each other.

```sh
pkg update && pkg upgrade
pkg install termux-api
```

Check that it works:

```sh
command -v termux-battery-status && termux-battery-status
command -v termux-notification
```

If `termux-battery-status` is missing, the Termux:API app is not installed or
is installed from a different source. The script prints exactly that and
exits 0.

Run the tests (they use stub commands, so no Termux:API is needed):

```sh
cd playground/battery-notify
bash tests/run.sh
```

## Usage

```sh
# Notify at or below 20 percent
bin/battery-notify

# Choose a different threshold
bin/battery-notify --threshold 30

# Print what would be sent, send nothing
bin/battery-notify --dry-run

# Forget the last notification so the next low reading notifies again
bin/battery-notify --reset
```

A daily check, run by `termux-job-scheduler` (see `termux-job-scheduler --help`
for the exact flags on your device):

```sh
termux-job-scheduler --period 3600 --job-id 1 \
    "$HOME/playground/battery-notify/bin/battery-notify --threshold 25"
```

Note that Android decides when a scheduled job actually runs. The script is
written to be safe when that happens late or more than once.

## Phone caveats

- **Termux:API is required.** Without the add-on app there is no battery
  reading and no notification. The script says so and exits 0.
- **Background jobs are not guaranteed.** `termux-job-scheduler` is a request
  to Android, not a guarantee. Vendors with aggressive battery management may
  delay or drop the job.
- **The notification fires per level.** If the battery goes from 15 to 14
  percent, you get a second notification. Use `--reset` if you want to be
  notified again at the same level.
- **Notification permission.** Android 13 and later ask the user to allow
  notifications. If you denied it, the notification is silently dropped.
- **Battery readings are approximate.** Android reports a rounded value, and
  the charging status lags reality by a second or two.

## Cleanup

```sh
rm -rf "$HOME/.local/state/battery-notify"
```

To remove the Termux:API package as well:

```sh
pkg uninstall termux-api
```

The add-on application itself is removed from Android's app settings.

## Safety notes

- The script never deletes files. `--reset` truncates its own state file.
- It only reads the battery and writes a notification. Nothing else is
  touched.
- No root, no system paths, no privileged ports.
- State is kept under `$HOME/.local/state/battery-notify`.
- It is idempotent: running it twice at the same battery level sends one
  notification, not two.
- The notification content contains no personal data.

## Sample output

With Termux:API installed and the battery at 80 percent:

```console
$ bin/battery-notify --threshold 20
battery-notify: battery 80% (CHARGING), threshold 20%
battery-notify: above threshold, no notification
```

At 15 percent, the first time:

```console
$ bin/battery-notify --threshold 20
battery-notify: battery 15% (DISCHARGING), threshold 20%
battery-notify: notified at 15%
```

At 15 percent again:

```console
$ bin/battery-notify --threshold 20
battery-notify: battery 15% (DISCHARGING), threshold 20%
battery-notify: already notified at 15%, staying quiet
```

Without Termux:API:

```console
$ bin/battery-notify
battery-notify: Termux:API is not available, so no battery reading was taken.
  Install the Termux:API add-on app (same source as Termux), then:
      pkg install termux-api
```

## Layout

```text
README.md       purpose, setup, usage, limitations
bin/            executable commands
src/            implementation
tests/          checks and sample data
.env.example    names of configuration values, never secrets
```
