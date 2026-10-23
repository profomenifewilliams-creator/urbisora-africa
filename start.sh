#!/bin/sh
set -eu
if [ -z "${SECRET_KEY:-}" ] && [ "${ALLOW_EPHEMERAL_SQLITE:-false}" = "true" ]; then
  SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
  export SECRET_KEY
fi
python manage.py migrate --run-syncdb --noinput
python manage.py collectstatic --noinput
python manage.py bootstrap_admin
exec gunicorn --preload config.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 2 --timeout 120
