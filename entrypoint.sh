#!/bin/bash

# Railway Port Configuration
PORT="${PORT:-8000}"
echo "🚀 Target Port: $PORT"

# 1. Run migrations in the background (prevents blocking web server)
echo "🔨 Applying migrations..."
python manage.py migrate --noinput &

# 2. Start Celery Worker & Beat (Low priority to save RAM for Web)
echo "👷 Starting Workers..."
# Use --concurrency 1 to save memory
celery -A Amaze worker --loglevel=info --pool=solo --concurrency=1 &
celery -A Amaze beat --loglevel=info &

# 3. Start Gunicorn (The most important process)
echo "🔥 Starting Gunicorn on 0.0.0.0:$PORT"
# Using 1 worker to stay under 512MB RAM (Chrome is heavy)
exec gunicorn Amaze.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 1 \
    --threads 4 \
    --timeout 120 \
    --log-level debug \
    --access-logfile - \
    --error-logfile -
