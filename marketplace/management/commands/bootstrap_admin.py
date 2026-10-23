import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Create the first Django superuser from configured environment variables; never overwrites an existing account."
    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
        if not username or not password:
            self.stdout.write("Admin bootstrap skipped: set DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD.")
            return
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={"email": email, "is_staff": True, "is_superuser": True, "is_active": True})
        if created:
            user.set_password(password)
            user.is_staff = user.is_superuser = user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created bootstrap administrator {username}."))
        else:
            self.stdout.write(f"Administrator {username} already exists; password was not changed.")
