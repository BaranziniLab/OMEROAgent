#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist
dir="dist/package"
mkdir -p "$dir"
cp manifest.json README.md pyproject.toml LICENSE NOTICE "$dir/"
if [ -f uv.lock ]; then cp uv.lock "$dir/"; fi
cp -R src "$dir/src"
cp -R skills "$dir/skills"
(
  cd "$dir"
  zip_entries="manifest.json README.md pyproject.toml LICENSE NOTICE src skills"
  if [ -f uv.lock ]; then zip_entries="manifest.json README.md pyproject.toml uv.lock LICENSE NOTICE src skills"; fi
  zip -qr "../omeroagent.brxt" $zip_entries -x '*/__pycache__/*' '*.pyc' '.venv/*'
)
rm -rf "$dir"
echo "dist/omeroagent.brxt"
