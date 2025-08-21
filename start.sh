#!/bin/sh



set -e
rm -rf /tmp/* && rm -rf /root/.cache
apt update && apt install -y -qq \
    tesseract-ocr \
    poppler-utils \
    build-essential \
    wkhtmltopdf \
&& apt clean && rm -rf /var/lib/apt/lists/* && rm -rf logs/ && rm -rf audit_logs/

uv venv .venv
. .venv/bin/activate
uv sync --no-cache-dir

# Run the app
exec uvicorn pnb.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips='*'
