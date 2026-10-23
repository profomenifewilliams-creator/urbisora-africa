# Urbisora Africa
**Property. People. Places.**

Urbisora Africa is a Django real-estate marketplace for property discovery, realtor profiles and portfolio management, client enquiries, and professional account workspaces.

## Member experience
- Immediate registration and sign-in without SMTP/email activation.
- Personal dashboard for property listings, saved properties, enquiry follow-up and profile management.
- CV-style realtor profiles with profile photos, title, agency, summary, specialties, languages, service areas and optional public contact links.
- Approved realtor profiles showcase their own publicly approved properties.
- Visitors can send messages from a public realtor profile; these go into that realtor's lead inbox.
- Listing owners can edit and archive their own properties. Edits return to moderation before republishing.
- Contact form saves messages to the platform admin inbox; outgoing email notification is not enabled in the no-SMTP release.

## Contact
- Phone: +234 906 791 2928
- Email: admin@ubisoraafrica.com
- Address: Guzape, FCT Abuja, Federal Housing Authority (FHA) Road, 219 House 15
- Developed and powered by Fortitech Digital Cluster.

## Useful routes
- Homepage: /
- Property search: /properties/
- Realtor directory: /realtors/
- Member dashboard: /dashboard/
- Profile editor: /profile/edit/
- Contact: /contact/
- Admin: /admin/
- Health check: /healthz/

## Render / migration notes
This repository includes a Render Docker service, PostgreSQL-aware settings, versioned database migrations, and Ansible smoke checks. The service currently has an explicit temporary SQLite fallback for demo launch; before real customer use, attach durable PostgreSQL and persistent object storage. Profile photo uploads currently live on the service filesystem and can be lost after a restart/redeploy. The existing free PostgreSQL test database expires and must not be treated as permanent backup or production storage.

Normal realtor membership activation is automatic. Identity/licence verification is separate and must not be assumed unless the platform has actually verified it.

## Local run
python -m venv .venv
pip install -r requirements.txt
python manage.py migrate --fake-initial
python manage.py runserver

## Checks
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test marketplace
