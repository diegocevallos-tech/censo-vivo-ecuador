#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
npm --prefix web ci
npm install --global mapshaper

printf 'Python: '; python --version
printf 'Node: '; node --version
printf 'gh: '; gh --version | head -n 1
printf 'duckdb: '; duckdb --version
printf 'tippecanoe: '; tippecanoe --version
printf 'mapshaper: '; mapshaper -v
printf 'pmtiles: '; pmtiles version
