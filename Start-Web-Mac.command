#!/bin/bash
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo "Please install Python 3.10 or newer from https://www.python.org/downloads/macos/"
  read -r -p "Press Enter to close..."
  exit 1
fi
if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)'; then
  echo "Python 3.10 or newer is required. Please update Python."
  read -r -p "Press Enter to close..."
  exit 1
fi
python3 run_web.py
