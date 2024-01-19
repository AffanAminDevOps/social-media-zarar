from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_monitoring.settings')

app = Celery('social_media_monitoring')
app.conf.enable_utc = False
# TIME_ZONE = ''
app.conf.update(timezone = 'Asia/Karachi')

app.config_from_object(settings, namespace='CELERY')

# Celery Beat Settings @shared_task(bind=True) 

app.conf.beat_schedule = {
    # 'keyword_crawling': {
    #     'task': 'social_media.tasks.ad_tracking_urdu_point',  # Replace with the actual path to your first task
    #     'schedule': 1800,  # 900 seconds = 15 minutes
    # }
    'add_tracking': {
        'task': 'social_media.tasks.ad_tracking_urdu_point',  # Replace with the actual path to your first task
        'schedule': 1800,  # 900 seconds = 15 minutes
    },
    'profile_crawling_nimar': {
        'task': 'social_media.tasks.profile_based_scraping_nimar',  # Replace with the actual path to your second task
        'schedule': 3600,  # 900 seconds = 15 minutes
    },
    'web_crawling_nimar': {
        'task': 'social_media.tasks.web_scrapers_nimar',  # Replace with the actual path to your second task
        'schedule': 9600,  # 900 seconds = 15 minutes
    },
}
# Celery Schedules - https://docs.celeryproject.org/en/stable/reference/celery.schedules.html

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')