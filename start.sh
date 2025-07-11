#!/bin/sh

# Optionally run migrations or other setup steps here

# Run the app
exec uvicorn pnb.main:app --host 0.0.0.0 --port 8000 --workers 2
