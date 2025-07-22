#!/bin/sh


# Run the app
apt update -y && apt install -y tesseract-ocr 
apt-get update -y && apt-get install -y poppler-utils 
exec uvicorn pnb.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips='*'
