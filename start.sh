#!/bin/sh

# Optionally run migrations or other setup steps here

# Run the app
uv venv .venv
. .venv/bin/activate
uv sync
uv pip install --system -r pyproject.toml --compile-bytecode
echo $OPENAI_API_KEY
exec python3 -m uvicorn pnb.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers
