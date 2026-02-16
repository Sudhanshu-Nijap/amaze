#!/bin/bash

# Ensure we are in the right directory
cd /app

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput || { echo "Migration failed!"; exit 1; }

# Start Celery Worker in the background (nohup prevents it from dying with the shell)
echo "Starting Celery Worker..."
nohup celery -A Amaze worker --loglevel=info --pool=solo > celery_worker.log 2>&1 &

# Start Celery Beat in the background
echo "Starting Celery Beat..."
nohup celery -A Amaze beat --loglevel=info > celery_beat.log 2>&1 &

# Brief sleep to let celery initialize
sleep 2

# Start Gunicorn (Web Server) in the foreground
# Binding to 0.0.0.0:$PORT is REQUIRED for Railway
echo "Starting Gunicorn on port ${PORT}..."
exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 120 --log-level debug Amaze.wsgi:application
