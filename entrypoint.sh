#!/bin/bash
set -e

python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn web.core.wsgi:application -c gunicorn.conf.py