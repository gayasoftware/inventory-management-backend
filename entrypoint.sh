#!/bin/sh

# Apply migrations
echo "Applying migrations..."
alembic upgrade head

# Attempt to generate a new migration based on model changes
# If no changes, env.py logic will skip file generation
echo "Checking for model changes..."
alembic revision --autogenerate -m "auto_sync"

# Start the application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
