#!/bin/bash
# HonKit book build script
# Copies content files into book/ working directory, builds, then cleans up.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$SCRIPT_DIR"

# Install dependencies if needed
if [ ! -d node_modules ]; then
  npm install
fi

# Copy content files into build workspace
cp "$ROOT_DIR/README.md" .
cp "$ROOT_DIR/SUMMARY.md" .
cp -r "$ROOT_DIR/reports" .

cleanup() {
  rm -f "$SCRIPT_DIR/README.md" "$SCRIPT_DIR/SUMMARY.md"
  rm -rf "$SCRIPT_DIR/reports"
}
trap cleanup EXIT

# Build
npx honkit build . _book

echo "Book built successfully → book/_book/"
