import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

app = Celery('web')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': 'redis://localhost:6379/0',
        'default_timeout': 60
    }
}

app.conf.beat_schedule = {
    'set-expired-payments': {
        'task': 'web.apps.payments.tasks.business.status.set_expired_payments',
        'schedule': 120,
    },
    'set-subscriptions-inactive-and-kick_users': {
        'task': (
            'web.apps.subscriptions.tasks.business'
            '.private_channel.set_subscriptions_inactive_and_kick_users_task'
        ),
        'schedule': 600,
    },
    'mass-mailing-expires-tomorrow-subscription': {
        'task': (
            'web.apps.subscriptions.tasks.business'
            '.private_channel.mass_mailing_expires_tomorrow_subscription_task'
        ),
        'schedule': crontab(hour=10, minute=0),
    },
}