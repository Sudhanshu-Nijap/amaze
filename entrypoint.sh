#!/bin/bash

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Start Celery Worker in the background
echo "Starting Celery Worker..."
celery -A Amaze worker --loglevel=info --pool=solo &

# Start Celery Beat in the background
echo "Starting Celery Beat..."
celery -A Amaze beat --loglevel=info &

# Start Gunicorn (Web Server) in the foreground
echo "Starting Gunicorn on port ${PORT:-8000}..."
echo "Web URL should be accessible soon."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 Amaze.wsgi:application
