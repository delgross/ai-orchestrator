#!/usr/bin/env bash
set -euo pipefail

# Always run from ~/ai regardless of where this is called from
cd "$(dirname "$0")"

# Activate venv
if [[ ! -d ".venv" ]]; then
  echo "ERROR: .venv not found in $(pwd)" >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# Compile the router to check for syntax errors
python -m py_compile router/router.py

echo "router/router.py compiled successfully"
