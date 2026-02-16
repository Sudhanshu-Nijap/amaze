#!/bin/bash
# Set default port
export PORT=${PORT:-8000}
echo "Starting Everything... Target Port: $PORT"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput || { echo "Migration failed!"; exit 1; }

# Start Celery Worker in the background
echo "Starting Celery Worker..."
celery -A Amaze worker --loglevel=info --pool=solo &

# Start Celery Beat in the background
echo "Starting Celery Beat..."
celery -A Amaze beat --loglevel=info &

# Start Gunicorn (Web Server) in the foreground
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 Amaze.wsgi:application
