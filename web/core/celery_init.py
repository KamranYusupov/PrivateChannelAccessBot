import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

app = Celery('web')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'set-expired-payments': {
        'task': 'web.apps.payments.tasks.business.status.set_expired_payments',
        'schedule': 120,
    },
}