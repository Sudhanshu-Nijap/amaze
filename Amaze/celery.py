from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module for 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Amaze.settings')

app = Celery('Amaze')
app.conf.broker_connection_retry_on_startup = True

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.beat_schedule = {
    'price_drop_notification_task': {
        'task': 'scraper.tasks.notify_price_drop',
        'schedule': crontab(minute='*/4'),
    }
    
}

# Discover tasks from all installed Django apps
app.autodiscover_tasks()
