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
        'schedule': 60,
    },
    'deactivate-subscriptions': {
        'task': (
            'web.apps.subscriptions.tasks.business.private_channel.deactivate_subscriptions_task'
        ),
        'schedule': 600,
    },
    'mass-kick-telegram-users-from-channel-with-inactive-subscription-task': {
        'task': (
            'web.apps.subscriptions.tasks.business'
            '.private_channel.mass_kick_telegram_users_from_channel_with_inactive_subscription_task'
        ),
        'schedule': 1800,
    },
    'mass-mailing-expires-tomorrow-subscription': {
        'task': (
            'web.apps.subscriptions.tasks.business'
            '.private_channel.mass_mailing_expires_tomorrow_subscription_task'
        ),
        'schedule': crontab(hour=14, minute=0),
    },
}