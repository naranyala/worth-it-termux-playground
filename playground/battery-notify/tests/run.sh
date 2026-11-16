#!/usr/bin/env sh
# Tests for the battery-notify experiment.
#
# The real termux-battery-status and termux-notification commands only exist
# with Termux:API installed, so these tests put stub commands on PATH.
#
# Usage: bash tests/run.sh

set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$here/.." && pwd)
script="$root/bin/battery-notify"

passed=0
failed=0

ok() {
    passed=$((passed + 1))
    printf 'ok   - %s\n' "$1"
}

not_ok() {
    failed=$((failed + 1))
    printf 'FAIL - %s\n' "$1"
}

check() {
    if [ "$2" = "$3" ]; then
        ok "$1"
    else
        not_ok "$1 (expected '$3', got '$2')"
    fi
}

check_contains() {
    case "$2" in
        *"$3"*) ok "$1" ;;
        *) not_ok "$1 (expected output containing '$3', got '$2')" ;;
    esac
}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT INT TERM

shell_bin=$(command -v sh)
stub_dir="$work/bin"
clean_dir="$work/clean"
state_dir="$work/state"
notifications="$work/notifications.txt"
battery_file="$work/battery.json"

mkdir -p "$stub_dir" "$clean_dir"

# A PATH with the usual utilities but without any termux-* command, used to
# test the graceful-degradation path.
for tool in tr sed head cat mkdir mv wc rm dirname sh; do
    tool_path=$(command -v "$tool" 2>/dev/null || true)
    if [ -n "$tool_path" ]; then
        ln -sf "$tool_path" "$clean_dir/$tool"
    fi
done

# --- stub termux-battery-status ---------------------------------------------
cat > "$stub_dir/termux-battery-status" <<'STUB'
#!/usr/bin/env sh
cat "$STUB_BATTERY_FILE"
STUB

cat > "$stub_dir/termux-notification" <<'STUB'
#!/usr/bin/env sh
printf '%s\n' "$*" >> "$STUB_NOTIFICATION_LOG"
STUB

chmod +x "$stub_dir/termux-battery-status" "$stub_dir/termux-notification"

export STUB_NOTIFICATION_LOG="$notifications"

run_notifier() {
    battery=$1
    shift
    printf '%s' "$battery" > "$battery_file"
    PATH="$stub_dir:$PATH" \
    STUB_BATTERY_FILE="$battery_file" \
    BATTERY_NOTIFY_STATE_DIR="$state_dir" \
        "$shell_bin" "$script" "$@" 2>&1
}

# --- help ---------------------------------------------------------------------
out=$(PATH="$stub_dir:$PATH" BATTERY_NOTIFY_STATE_DIR="$state_dir" "$shell_bin" "$script" --help)
code=$?
check "--help exits 0" "$code" "0"
check_contains "--help prints usage" "$out" "Usage: battery-notify"

# --- invalid input ------------------------------------------------------------
set +e
run_notifier '{"percentage":50}' --threshold abc >/dev/null 2>&1
code=$?
set -e
check "invalid threshold exits non-zero" "$code" "2"

set +e
run_notifier '{"percentage":50}' --nope >/dev/null 2>&1
code=$?
set -e
check "unknown option exits non-zero" "$code" "2"

set +e
run_notifier '{"percentage":50}' --threshold 200 >/dev/null 2>&1
code=$?
set -e
check "out of range threshold exits non-zero" "$code" "2"

# --- graceful degradation when Termux:API is missing -------------------------
set +e
out=$(PATH="$clean_dir" BATTERY_NOTIFY_STATE_DIR="$state_dir" "$shell_bin" "$script" 2>&1)
code=$?
set -e
check "missing Termux:API exits 0" "$code" "0"
check_contains "missing Termux:API explains itself" "$out" "Termux:API is not available"
check_contains "missing Termux:API names the package" "$out" "pkg install termux-api"

# --- above the threshold, no notification ------------------------------------
rm -f "$notifications"
out=$(run_notifier '{"percentage":80,"status":"CHARGING"}' --threshold 20)
check_contains "above threshold reports the level" "$out" "battery 80%"
check_contains "above threshold does not notify" "$out" "above threshold, no notification"
if [ -f "$notifications" ]; then
    not_ok "above threshold wrote no notification"
else
    ok "above threshold wrote no notification"
fi

# --- below the threshold, notification sent ----------------------------------
out=$(run_notifier '{"percentage":15,"status":"DISCHARGING"}' --threshold 20)
check_contains "below threshold notifies" "$out" "notified at 15%"
if [ -f "$notifications" ]; then
    ok "notification was written"
    check_contains "notification has a title" "$(cat "$notifications")" "Battery 15%"
else
    not_ok "notification was written"
fi

# --- idempotent: same level again stays quiet --------------------------------
out=$(run_notifier '{"percentage":15,"status":"DISCHARGING"}' --threshold 20)
check_contains "second run stays quiet" "$out" "already notified at 15%"
check "only one notification recorded" "$(wc -l < "$notifications" | tr -d ' ')" "1"

# --- dry run sends nothing ---------------------------------------------------
out=$(run_notifier '{"percentage":10,"status":"DISCHARGING"}' --threshold 20 --dry-run)
check_contains "dry run reports what it would do" "$out" "dry run, would notify"
if [ -f "$notifications" ]; then
    check "dry run wrote no notification" "$(wc -l < "$notifications" | tr -d ' ')" "1"
else
    ok "dry run wrote no notification"
fi

# --- reset clears the state --------------------------------------------------
run_notifier '{"percentage":15,"status":"DISCHARGING"}' --threshold 20 >/dev/null
out=$(run_notifier '{"percentage":15,"status":"DISCHARGING"}' --threshold 20 --reset)
check_contains "reset reports" "$out" "reset notification state"

# --- unreadable battery output is handled ------------------------------------
out=$(run_notifier '' --threshold 20)
check_contains "empty battery output is handled" "$out" "returned no output"

printf '\n%s passed, %s failed\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
