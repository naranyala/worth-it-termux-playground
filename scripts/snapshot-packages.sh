#!/usr/bin/env bash
#
# snapshot-packages.sh — record the package list of the current Termux
# environment so it can be reinstalled later.
#
# Writes two files into the output directory (default: the current directory):
#   termux-packages.txt       from 'pkg list-installed'
#   termux-manual-packages.txt from 'apt-mark showmanual'
#
# Both files are machine specific and are therefore git-ignored.

set -euo pipefail

readonly SCRIPT_NAME="$(basename "$0")"
OUT_DIR="."

usage() {
  cat <<EOF
${SCRIPT_NAME} — snapshot the installed Termux packages.

USAGE
  ${SCRIPT_NAME} [--out <dir>]

OPTIONS
  --out <dir>   Directory to write the snapshot files into (default: ".")
                The directory is created if it does not exist.
  -h, --help    Show this help and exit.

FILES
  termux-packages.txt         output of 'pkg list-installed'
  termux-manual-packages.txt  output of 'apt-mark showmanual'

EXAMPLES
  ${SCRIPT_NAME}
  ${SCRIPT_NAME} --out ~/snapshots/2026-01-01
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --out)
      [ "$#" -ge 2 ] || { printf '%s\n' "${SCRIPT_NAME}: --out requires a directory" >&2; exit 2; }
      OUT_DIR="$2"; shift ;;
    --out=*)
      OUT_DIR="${1#--out=}"; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      usage >&2; printf '%s: unknown option: %s\n' "$SCRIPT_NAME" "$1" >&2; exit 2 ;;
  esac
  shift
done

if ! command -v pkg >/dev/null 2>&1; then
  printf '%s: ERROR: %s is not available; run this inside Termux.\n' "$SCRIPT_NAME" "pkg" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

pkg_file="${OUT_DIR}/termux-packages.txt"
manual_file="${OUT_DIR}/termux-manual-packages.txt"

# Write to a temporary file and move it into place, so an interrupted run
# never leaves a half-written snapshot behind.
tmp_pkg="$(mktemp "${OUT_DIR}/.termux-packages.XXXXXX")"
tmp_manual="$(mktemp "${OUT_DIR}/.termux-manual.XXXXXX")"
cleanup() {
  rm -f "$tmp_pkg" "$tmp_manual"
}
trap cleanup EXIT

printf '[%s] writing %s\n' "$SCRIPT_NAME" "$pkg_file"
pkg list-installed > "$tmp_pkg"
mv "$tmp_pkg" "$pkg_file"
chmod 644 "$pkg_file" 2>/dev/null || true

printf '[%s] writing %s\n' "$SCRIPT_NAME" "$manual_file"
if command -v apt-mark >/dev/null 2>&1; then
  apt-mark showmanual > "$tmp_manual"
else
  printf '[%s] WARNING: apt-mark not found; writing an empty manual list.\n' "$SCRIPT_NAME" >&2
  : > "$tmp_manual"
fi
mv "$tmp_manual" "$manual_file"
chmod 644 "$manual_file" 2>/dev/null || true
trap - EXIT

pkg_count=$(grep -c . "$pkg_file" || true)
manual_count=$(grep -c . "$manual_file" || true)

cat <<EOF

--------------------------------------------------------------
${SCRIPT_NAME} summary
--------------------------------------------------------------
  output directory : ${OUT_DIR}
  installed pkgs   : ${pkg_count} line(s) in termux-packages.txt
  manual pkgs      : ${manual_count} line(s) in termux-manual-packages.txt

Restore later with:
  ./scripts/restore.sh --dir ${OUT_DIR}
--------------------------------------------------------------
EOF
