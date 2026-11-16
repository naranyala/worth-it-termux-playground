#!/usr/bin/env sh
# battery-notify - notify when the battery drops below a threshold.
#
# Needs the Termux:API add-on application and the `termux-api` package.
# Without them the script explains what is missing and exits 0, so a scheduled
# job does not fill the log with errors.
#
# POSIX sh. Must pass `bash -n`.

set -eu

PROG=battery-notify
DEFAULT_THRESHOLD=20
STATE_DIR="${BATTERY_NOTIFY_STATE_DIR:-$HOME/.local/state/battery-notify}"
STATE_FILE="$STATE_DIR/last-notified"

usage() {
    cat <<'EOF'
Usage: battery-notify [--threshold PERCENT] [--dry-run] [--reset]

Send a phone notification when the battery falls to or below a threshold.

Options:
  --threshold PERCENT   Notify at or below this percentage (default: 20).
  --dry-run             Print what would be sent, send nothing.
  --reset               Forget the last notification and exit.
  -h, --help            Show this help and exit.

Environment:
  BATTERY_NOTIFY_THRESHOLD   Default threshold percentage.
                             Default: 20
  BATTERY_NOTIFY_STATE_DIR   Where the last-notification state is kept.
                             Default: $HOME/.local/state/battery-notify
EOF
}

die() {
    printf '%s: %s\n' "$PROG" "$1" >&2
    exit "${2:-2}"
}

threshold=${BATTERY_NOTIFY_THRESHOLD:-$DEFAULT_THRESHOLD}
dry_run=0
reset=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --threshold)
            [ "$#" -ge 2 ] || die "--threshold needs a value"
            threshold=$2
            shift 2
            ;;
        --threshold=*)
            threshold=${1#--threshold=}
            shift
            ;;
        --dry-run)
            dry_run=1
            shift
            ;;
        --reset)
            reset=1
            shift
            ;;
        --)
            shift
            break
            ;;
        -*)
            die "unknown option: $1"
            ;;
        *)
            die "unexpected argument: $1"
            ;;
    esac
done

[ "$#" -eq 0 ] || die "unexpected argument: $1"

case "$threshold" in
    ''|*[!0-9]*)
        die "threshold must be a whole number, got: $threshold"
        ;;
esac
[ "$threshold" -le 100 ] || die "threshold must be between 0 and 100"
[ "$threshold" -ge 0 ] || die "threshold must be between 0 and 100"

if [ "$reset" -eq 1 ]; then
    # Truncate rather than delete: the script never removes files.
    mkdir -p "$STATE_DIR"
    : > "$STATE_FILE"
    printf '%s: reset notification state\n' "$PROG"
    exit 0
fi

# --- Termux:API checks -------------------------------------------------------

if ! command -v termux-battery-status >/dev/null 2>&1; then
    printf '%s: Termux:API is not available, so no battery reading was taken.\n' "$PROG"
    printf '  Install the Termux:API add-on app (same source as Termux), then:\n'
    printf '      pkg install termux-api\n'
    exit 0
fi

if ! command -v termux-notification >/dev/null 2>&1; then
    printf '%s: termux-notification is not available, so nothing can be notified.\n' "$PROG"
    printf '  Install it with: pkg install termux-api\n'
    exit 0
fi

# --- Read the battery --------------------------------------------------------

status_json=$(termux-battery-status 2>/dev/null || true)

if [ -z "$status_json" ]; then
    printf '%s: termux-battery-status returned no output.\n' "$PROG"
    exit 0
fi

# termux-battery-status prints JSON. Extract the fields we need without jq,
# so the script has no dependencies beyond coreutils.
extract_json_string() {
    printf '%s' "$status_json" \
        | tr ',' '\n' \
        | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" \
        | head -n 1
}

extract_json_number() {
    printf '%s' "$status_json" \
        | tr ',' '\n' \
        | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p" \
        | head -n 1
}

percentage=$(extract_json_number percentage)
state=$(extract_json_string status)

if [ -z "$percentage" ]; then
    printf '%s: could not read a percentage from termux-battery-status.\n' "$PROG"
    printf '  Raw output: %s\n' "$status_json"
    exit 0
fi

[ -n "$state" ] || state=UNKNOWN

printf '%s: battery %s%% (%s), threshold %s%%\n' "$PROG" "$percentage" "$state" "$threshold"

if [ "$percentage" -gt "$threshold" ]; then
    # Above the threshold: record that we are fine and stop.
    printf '%s: above threshold, no notification\n' "$PROG"
    exit 0
fi

# --- Idempotency -------------------------------------------------------------
# Notify once per crossing. The state file holds the level that was last
# notified, so repeated runs at the same low level stay quiet.

if [ -f "$STATE_FILE" ]; then
    last=$(cat "$STATE_FILE" 2>/dev/null || printf '')
else
    last=''
fi

if [ "$last" = "$percentage" ]; then
    printf '%s: already notified at %s%%, staying quiet\n' "$PROG" "$percentage"
    exit 0
fi

title="Battery $percentage%"
body="Battery is at $percentage%. Plug in a charger."

if [ "$dry_run" -eq 1 ]; then
    printf '%s: dry run, would notify:\n' "$PROG"
    printf '  title:   %s\n' "$title"
    printf '  content: %s\n' "$body"
    exit 0
fi

if termux-notification --title "$title" --content "$body" >/dev/null 2>&1; then
    mkdir -p "$STATE_DIR"
    tmp="$STATE_FILE.tmp.$$"
    printf '%s\n' "$percentage" > "$tmp"
    mv "$tmp" "$STATE_FILE"
    printf '%s: notified at %s%%\n' "$PROG" "$percentage"
else
    printf '%s: termux-notification failed.\n' "$PROG"
    exit 0
fi
