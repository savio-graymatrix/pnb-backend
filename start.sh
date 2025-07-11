#!/bin/sh

# Optionally run migrations or other setup steps here

# Run the app
uv venv .venv
source .venv/bin/activate
uv sync
exec uvicorn pnb.main:app --host 0.0.0.0 --port 8000 --workers 2
