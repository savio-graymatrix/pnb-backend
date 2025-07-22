#!/bin/sh

# Optionally run migrations or other setup steps here

# Run the app
apt update -y && apt install -y tesseract-ocr 
apt-get update -y && apt-get install -y poppler-utils 
rm -rf /root/.cache && rm -rf /tmp/*
uv venv .venv
. .venv/bin/activate
uv pip install --system -r pyproject.toml --compile-bytecode --no-cache-dir
exec uvicorn pnb.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips='*'
