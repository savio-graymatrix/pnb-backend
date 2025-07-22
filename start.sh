#!/bin/sh

set -e
uv venv .venv
. .venv/bin/activate
uv sync --no-cache-dir --compiled-bytecode

# Run the app
exec uvicorn pnb.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips='*'
