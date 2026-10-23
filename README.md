# Urbisora Africa

**Property. People. Places.**

Django-powered real-estate marketplace with immediate account registration, public property search, authorised listing submissions, enquiry capture, saved properties, realtor applications and an admin moderation area.

## Render deployment

The repository contains a Dockerfile and Render configuration. Registration does not require SMTP or email verification. Owner-authorised listings stay pending until a staff administrator approves them in Django admin.

- Health endpoint: `/healthz/`
- Admin: `/admin/`
- Property directory: `/properties/`
- Member dashboard: `/dashboard/`

The bootstrap command reads `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, and `DJANGO_SUPERUSER_PASSWORD`. Set a strong unique password in Render's environment settings.

## Initial free-tier limitation

For a direct initial deployment, SQLite defaults to `/tmp/urbisora.sqlite3` until a persistent PostgreSQL connection is configured. Free Render local storage is ephemeral and may be lost after a restart or redeploy. Property imagery uses external image URLs in this initial build. Attach a durable database and persistent object storage before commercial use.

## Local development

```bash
python -m venv .venv
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py runserver
```

Run application tests with `python manage.py test marketplace`. Post-deployment HTTP smoke checks are in `ansible/verify-deployment.yml`.
