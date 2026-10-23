#!/bin/sh
set -eu
python manage.py migrate --run-syncdb --noinput
python manage.py collectstatic --noinput
python manage.py bootstrap_admin
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 2 --timeout 120
