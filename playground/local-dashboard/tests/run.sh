#!/usr/bin/env sh
# Run the local-dashboard test suite with the Python standard library only.
# Usage: bash tests/run.sh

set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$here/.." && pwd)

PYTHON=${PYTHON:-python3}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    printf 'run.sh: python3 was not found on PATH. Install it with: pkg install python\n' >&2
    exit 127
fi

cd "$root"
exec "$PYTHON" -m unittest discover -s tests -v
