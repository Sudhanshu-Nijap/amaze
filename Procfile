release: python manage.py migrate
web: daphne Amaze.asgi:application --port $PORT --bind 0.0.0.0 -v2
celery: celery -A Amaze.celery worker -l info
celerybeat: celery -A Amaze beat -l INFO 
celeryworker2: celery -A Amaze.celery worker & celery -A Amaze beat -l INFO & wait -n