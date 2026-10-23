# Urbisora Africa

**Property. People. Places.**

Django-powered real-estate marketplace with immediate account registration, public property search, authorised listing submissions, enquiry capture, saved properties, realtor applications and an admin moderation area.

## Render deployment

This repository includes a Dockerfile and Render Blueprint. Once Render is connected to this private GitHub repository, use **New → Blueprint** in Render and select this repository.

- Registration is immediate; no SMTP or email activation is required.
- Health endpoint: `/healthz/`
- Admin: `/admin/`
- Property directory: `/properties/`
- Member dashboard: `/dashboard/`
- Listings need owner/agent authorisation and staff approval before public publication.
- The bootstrap command reads `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, and `DJANGO_SUPERUSER_PASSWORD`. The Blueprint generates the secret key and initial admin password; read the generated value from Render environment settings and store it privately.

## Initial free-tier limitations

The Blueprint is configured to link to the existing free database named `urbisora-africa-db`. Free databases have an expiry window and must not be assumed to be permanent production storage. If the Blueprint cannot adopt the existing database, resolve the name conflict in Render before syncing rather than creating a paid resource automatically.

Free Render containers have ephemeral local filesystems. Property image links can point at externally hosted images, but uploaded files stored locally will not be durable across restarts. Use persistent object storage for commercial production.

## Local development

```bash
python -m venv .venv
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py runserver
```

Run application tests with `python manage.py test marketplace`. Post-deployment HTTP smoke checks are in `ansible/verify-deployment.yml`.
