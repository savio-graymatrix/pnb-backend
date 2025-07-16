#!/bin/sh

# Optionally run migrations or other setup steps here

# Run the app
sudo apt-get install -y tesseract-ocr 
sudo apt get install -y poppler-utils libpoppler-cpp-dev
export PATH="/usr/bin:$PATH"
echo $PATH
whereis pdfinfo
uv venv .venv
. .venv/bin/activate
uv sync
uv pip install --system -r pyproject.toml --compile-bytecode
rm -rf /root/.cache /tmp/*
du -hs /root
exec python3 -m uvicorn pnb.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips='*'
