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
    'set-subscriptions-inactive-and-kick_users': {
        'task': (
            'web.apps.subscriptions.tasks.business'
            '.private_channel.set_subscriptions_inactive_and_kick_users'
        ),
        'schedule': 600,
    },
}