#!/bin/bash

# Configuration
PORT="${PORT:-8000}"
echo "------------------------------------------------"
echo "🚀 Startup Profile: Production"
echo "🌐 Port: $PORT"
echo "------------------------------------------------"

# Run migrations in the background but wait for them briefly
echo "🔨 Running Migrations..."
python manage.py migrate --noinput &
MIGRATION_PID=$!

# Start Celery Worker & Beat in the background
echo "👷 Starting Background Tasks (Worker & Beat)..."
celery -A Amaze worker --loglevel=info --pool=solo &
celery -A Amaze beat --loglevel=info &

# Wait for migrations to finish for up to 15 seconds
wait $MIGRATION_PID
echo "✅ Migrations complete or moved to background."

# Start Gunicorn
echo "🔥 Starting Web Server (Gunicorn)..."
# We bind specifically to 0.0.0.0:$PORT
# Reduced workers to save RAM (Railway single service limits)
exec gunicorn Amaze.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
