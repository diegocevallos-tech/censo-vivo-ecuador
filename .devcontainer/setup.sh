#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
npm --prefix web ci
npm install --global mapshaper
go install github.com/protomaps/go-pmtiles@latest

printf 'Python: '; python --version
printf 'Node: '; node --version
printf 'gh: '; gh --version | head -n 1
printf 'tippecanoe: '; tippecanoe --version
printf 'mapshaper: '; mapshaper -v
printf 'pmtiles: '; "$(go env GOPATH)/bin/pmtiles" --help | head -n 1
