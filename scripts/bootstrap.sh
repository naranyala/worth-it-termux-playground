#!/usr/bin/env bash
#
# bootstrap.sh — idempotent, non-interactive Termux bootstrap.
#
# Installs the base packages the Termux Playground experiments expect, and
# optionally the Pi coding agent. Safe to re-run: every step is additive and
# nothing is ever removed or overwritten destructively.
#
# Usage:
#   ./scripts/bootstrap.sh [options]
#
# Run on a Termux device (Android). It never uses sudo, never deletes
# anything, and never runs an interactive prompt unless you explicitly ask
# for it with --with-storage.

set -euo pipefail

readonly SCRIPT_NAME="$(basename "$0")"

# ---------------------------------------------------------------- defaults --
WITH_PI=0
WITH_PYTHON=1
WITH_STORAGE=0
NO_UPDATE=0
DRY_RUN=0

readonly BASE_PACKAGES=(git curl wget nano vim tmux man termux-tools)
readonly PYTHON_PACKAGES=(python)
readonly PI_PACKAGES=(nodejs npm)
readonly PI_NPM_PACKAGE="@earendil-works/pi-coding-agent"

# ---------------------------------------------------------------- helpers --
usage() {
  cat <<EOF
${SCRIPT_NAME} — bootstrap a Termux environment for the Termux Playground.

USAGE
  ${SCRIPT_NAME} [options]

OPTIONS
  --with-pi          Also install Node.js, npm and the Pi coding agent
                     (${PI_NPM_PACKAGE}). Default: off.
  --without-pi       Do not install Pi (default).
  --with-python      Install Python (default: on).
  --without-python   Skip Python installation.
  --with-storage     Run 'termux-setup-storage' (INTERACTIVE — it asks for
                     storage permission). Never runs unless you pass this.
  --no-update        Skip 'pkg update && pkg upgrade'.
  --dry-run          Print the commands that would run, without running them.
  -h, --help         Show this help and exit.

BEHAVIOUR
  * Idempotent: re-running only installs what is missing.
  * Never uses sudo and never deletes or removes anything.
  * 'termux-setup-storage' is interactive, so it is opt-in only. When it is
    not requested, clear instructions are printed instead.
  * 'pkg update && pkg upgrade' runs unless --no-update is given.

EXAMPLES
  ${SCRIPT_NAME}                     # base packages only
  ${SCRIPT_NAME} --with-pi           # base packages + Pi coding agent
  ${SCRIPT_NAME} --dry-run           # show the plan, change nothing
EOF
}

log()  { printf '[%s] %s\n' "$SCRIPT_NAME" "$*"; }
warn() { printf '[%s] WARNING: %s\n' "$SCRIPT_NAME" "$*" >&2; }
die()  { printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }

# Run a command, or just print it when --dry-run is active.
run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '[%s] DRY-RUN: %s\n' "$SCRIPT_NAME" "$*"
  else
    log "running: $*"
    "$@"
  fi
}

# Run a shell snippet through bash -c (needed for pipelines).
run_sh() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '[%s] DRY-RUN: %s\n' "$SCRIPT_NAME" "$1"
  else
    log "running: %s" "$1"
    bash -c "$1"
  fi
}

is_installed() {
  # Returns 0 when the given package is already installed.
  if command -v dpkg-query >/dev/null 2>&1; then
    dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "ok installed" && return 0
    return 1
  fi
  if command -v pkg >/dev/null 2>&1; then
    pkg list-installed 2>/dev/null | grep -q "^${1}/" && return 0
    return 1
  fi
  return 1
}

install_packages() {
  # install_packages <pkg> [pkg...] — installs only the missing ones.
  local missing=()
  local pkgname
  for pkgname in "$@"; do
    if is_installed "$pkgname"; then
      log "already installed: ${pkgname}"
    else
      missing+=("$pkgname")
    fi
  done

  if [ "${#missing[@]}" -eq 0 ]; then
    log "nothing to install for: $*"
    return 0
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    printf '[%s] DRY-RUN: pkg install -y %s\n' "$SCRIPT_NAME" "${missing[*]}"
    return 0
  fi

  log "installing: ${missing[*]}"
  # -y keeps this non-interactive; apt/pkg is safe to re-run.
  pkg install -y "${missing[@]}"
}

# ------------------------------------------------------------------ args ---
while [ "$#" -gt 0 ]; do
  case "$1" in
    --with-pi)        WITH_PI=1 ;;
    --without-pi)     WITH_PI=0 ;;
    --with-python)    WITH_PYTHON=1 ;;
    --without-python) WITH_PYTHON=0 ;;
    --with-storage)   WITH_STORAGE=1 ;;
    --no-update)      NO_UPDATE=1 ;;
    --dry-run)        DRY_RUN=1 ;;
    -h|--help)        usage; exit 0 ;;
    *)                usage >&2; die "unknown option: $1" ;;
  esac
  shift
done

# ------------------------------------------------------------ environment ---
if [ "$DRY_RUN" -eq 0 ]; then
  if ! command -v pkg >/dev/null 2>&1; then
    die "the 'pkg' command was not found. This script must run inside Termux."
  fi
fi

if [ "${PREFIX:-}" = "" ] && [ "$DRY_RUN" -eq 0 ]; then
  warn "\$PREFIX is not set — this does not look like a Termux environment."
fi

# ----------------------------------------------------------------- steps ---
if [ "$DRY_RUN" -eq 1 ]; then
  log "starting bootstrap (dry run — nothing will be installed)"
else
  log "starting bootstrap"
fi

if [ "$NO_UPDATE" -eq 0 ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '[%s] DRY-RUN: pkg update && pkg upgrade\n' "$SCRIPT_NAME"
  else
    log "updating package lists and upgrading installed packages"
    pkg update
    pkg upgrade
  fi
else
  log "skipping pkg update/upgrade (--no-update)"
fi

log "base packages: ${BASE_PACKAGES[*]}"
install_packages "${BASE_PACKAGES[@]}"

if [ "$WITH_PYTHON" -eq 1 ]; then
  log "python packages: ${PYTHON_PACKAGES[*]}"
  install_packages "${PYTHON_PACKAGES[@]}"
else
  log "skipping python (--without-python)"
fi

if [ "$WITH_PI" -eq 1 ]; then
  log "pi packages: ${PI_PACKAGES[*]}"
  install_packages "${PI_PACKAGES[@]}"

  if [ "$DRY_RUN" -eq 1 ]; then
    printf '[%s] DRY-RUN: npm install -g --ignore-scripts %s\n' "$SCRIPT_NAME" "$PI_NPM_PACKAGE"
  else
    # --ignore-scripts keeps the install from running arbitrary lifecycle
    # scripts, which matters on a phone.
    log "installing ${PI_NPM_PACKAGE} via npm"
    npm install -g --ignore-scripts "$PI_NPM_PACKAGE"
  fi
else
  log "skipping pi coding agent (use --with-pi to install it)"
fi

if [ "$WITH_STORAGE" -eq 1 ]; then
  warn "running termux-setup-storage — this is interactive; grant the permission prompt."
  run termux-setup-storage
else
  cat <<'EOF'
Storage access was NOT enabled (termux-setup-storage is interactive and is
never run automatically). If you need shared-storage access, run this once,
by hand, and accept the Android permission dialog:

    termux-setup-storage

Afterwards the shared storage shows up under ~/storage (for example
~/storage/downloads and ~/storage/shared).
EOF
fi

# --------------------------------------------------------------- summary ---
cat <<EOF

--------------------------------------------------------------
${SCRIPT_NAME} summary
--------------------------------------------------------------
  update/upgrade   : $([ "$NO_UPDATE" -eq 1 ] && echo "skipped" || echo "$([ "$DRY_RUN" -eq 1 ] && echo "would run" || echo "ran")")
  base packages    : ${BASE_PACKAGES[*]}
  python           : $([ "$WITH_PYTHON" -eq 1 ] && echo "planned (${PYTHON_PACKAGES[*]})" || echo "skipped")
  pi coding agent  : $([ "$WITH_PI" -eq 1 ] && echo "planned (${PI_NPM_PACKAGE})" || echo "skipped")
  storage setup    : $([ "$WITH_STORAGE" -eq 1 ] && echo "ran termux-setup-storage" || echo "not run (run it manually if needed)")
  dry run          : $([ "$DRY_RUN" -eq 1 ] && echo yes || echo no)

Next steps:
  * Snapshot your environment: ./scripts/snapshot-packages.sh
  * Read the catalog:            README.md
--------------------------------------------------------------
EOF

log "done"
