#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <pypi|testpypi>"
  exit 1
fi

REPO="$1"
if [[ "$REPO" != "pypi" && "$REPO" != "testpypi" ]]; then
  echo "Repository must be 'pypi' or 'testpypi'."
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d dist ]]; then
  echo "dist/ not found. Run scripts/build_dist.sh first."
  exit 1
fi

python -m pip install --quiet -r requirements-release.txt
python -m twine check dist/*
python -m twine upload --repository "$REPO" dist/*
