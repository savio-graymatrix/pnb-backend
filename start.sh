#!/bin/sh

set -e

# Run the app
exec uvicorn pnb.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips='*'
