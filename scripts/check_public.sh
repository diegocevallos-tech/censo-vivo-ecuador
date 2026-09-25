#!/usr/bin/env bash
set -euo pipefail

python --version
node --version
duckdb --version
pmtiles version
tippecanoe --version
mapshaper -v
python -m pytest tests -q
npm --prefix web ci
npm --prefix web run build
