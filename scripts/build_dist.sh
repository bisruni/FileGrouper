#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements-release.txt

rm -rf dist build *.egg-info
python -m build --sdist --wheel .
python -m twine check dist/*

echo "[release] distribution artifacts created under dist/"
