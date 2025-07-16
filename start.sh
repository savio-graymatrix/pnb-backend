#!/bin/sh

# Optionally run migrations or other setup steps here

# Run the app
sudo apt install -y tesseract-ocr 
sudo apt-get install -y poppler-utils 
whereis pdfinfo
uv venv .venv
. .venv/bin/activate
uv sync
rm -rf /root/.cache /tmp/*
exec python3 -m uvicorn pnb.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips='*'
