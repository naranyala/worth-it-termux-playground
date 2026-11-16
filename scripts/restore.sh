#!/usr/bin/env bash
#
# restore.sh — reinstall the packages recorded by scripts/snapshot-packages.sh.
#
# The restore path is:
#   1. scripts/snapshot-packages.sh  -> termux-packages.txt / termux-manual-packages.txt
#   2. scripts/restore.sh --dir <snapshot dir>
#
# Packages that are already installed are skipped, so the script is safe to
# run repeatedly and on a partially-restored device.

set -euo pipefail

readonly SCRIPT_NAME="$(basename "$0")"
SNAPSHOT_DIR=""
DRY_RUN=0

usage() {
  cat <<EOF
${SCRIPT_NAME} — reinstall packages from a Termux snapshot.

USAGE
  ${SCRIPT_NAME} --dir <snapshot-dir> [options]

OPTIONS
  --dir <dir>     Directory containing termux-packages.txt and/or
                  termux-manual-packages.txt (required).
  --dry-run       Print what would be installed, change nothing.
  -h, --help      Show this help and exit.

NOTES
  * 'termux-manual-packages.txt' (from 'apt-mark showmanual') is preferred
    because it contains plain package names.
  * 'termux-packages.txt' (from 'pkg list-installed') is used as a fallback;
    its 'name/stable-installed version arch' lines are reduced to names.
  * Packages already installed are skipped, so re-running is safe.
  * Nothing is ever removed or downgraded.

EXAMPLES
  ${SCRIPT_NAME} --dir ~/snapshots/2026-01-01
  ${SCRIPT_NAME} --dir ./snapshots --dry-run
EOF
}

die() { printf '%s: ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }
log() { printf '[%s] %s\n' "$SCRIPT_NAME" "$*"; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dir)
      [ "$#" -ge 2 ] || die "--dir requires a directory"
      SNAPSHOT_DIR="$2"; shift ;;
    --dir=*)
      SNAPSHOT_DIR="${1#--dir=}"; shift ;;
    --dry-run)
      DRY_RUN=1 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      usage >&2; die "unknown option: $1" ;;
  esac
  shift
done

[ -n "$SNAPSHOT_DIR" ] || { usage >&2; die "--dir is required"; }
[ -d "$SNAPSHOT_DIR" ] || die "snapshot directory not found: ${SNAPSHOT_DIR}"

MANUAL_FILE="${SNAPSHOT_DIR}/termux-manual-packages.txt"
PKG_FILE="${SNAPSHOT_DIR}/termux-packages.txt"

[ -f "$MANUAL_FILE" ] || [ -f "$PKG_FILE" ] || \
  die "no termux-packages.txt or termux-manual-packages.txt found in ${SNAPSHOT_DIR}"

if [ "$DRY_RUN" -eq 0 ] && ! command -v pkg >/dev/null 2>&1; then
  die "the 'pkg' command was not found; run this inside Termux."
fi

# Collect package names into a sorted, de-duplicated list.
collect_packages() {
  if [ -f "$MANUAL_FILE" ]; then
    sed -e 's/#.*$//' -e 's/[[:space:]]*$//' "$MANUAL_FILE" | grep -v '^$' || true
  fi
  if [ -f "$PKG_FILE" ]; then
    # Lines look like: git/stable-installed 2.43.0-1 all
    sed -e 's/[[:space:]].*$//' -e 's|/.*$||' -e 's/[[:space:]]*$//' "$PKG_FILE" \
      | grep -v '^$' | grep -v '^Listing' || true
  fi
}

is_installed() {
  if command -v dpkg-query >/dev/null 2>&1; then
    dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "ok installed"
    return
  fi
  if command -v pkg >/dev/null 2>&1; then
    pkg list-installed 2>/dev/null | grep -q "^${1}/"
    return
  fi
  return 1
}

log "reading snapshot from ${SNAPSHOT_DIR}"

ALL_PACKAGES=$(collect_packages | sort -u)
TOTAL=$(printf '%s\n' "$ALL_PACKAGES" | grep -c . || true)

if [ "$TOTAL" -eq 0 ]; then
  log "no packages found in the snapshot; nothing to do."
else
  MISSING=""
  SKIPPED=0
  while IFS= read -r pkgname; do
    [ -n "$pkgname" ] || continue
    if is_installed "$pkgname"; then
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
    MISSING="${MISSING}${pkgname}"$'\n'
  done <<EOF
${ALL_PACKAGES}
EOF

  MISSING_COUNT=$(printf '%s' "$MISSING" | grep -c . || true)

  if [ "$MISSING_COUNT" -eq 0 ]; then
    log "all ${TOTAL} package(s) are already installed; nothing to do."
  elif [ "$DRY_RUN" -eq 1 ]; then
    log "dry run: would install ${MISSING_COUNT} package(s):"
    printf '%s' "$MISSING" | sed 's/^/  - /'
  else
    log "installing ${MISSING_COUNT} package(s):"
    printf '%s' "$MISSING" | sed 's/^/  - /'
    # shellcheck disable=SC2086
    printf '%s' "$MISSING" | grep . | xargs -r pkg install -y
  fi
fi

cat <<EOF

--------------------------------------------------------------
${SCRIPT_NAME} summary
--------------------------------------------------------------
  snapshot dir  : ${SNAPSHOT_DIR}
  packages seen : ${TOTAL}
  dry run       : $([ "$DRY_RUN" -eq 1 ] && echo yes || echo no)

Nothing was removed or downgraded. Re-running this script is safe.
--------------------------------------------------------------
EOF
