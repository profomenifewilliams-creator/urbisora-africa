from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("client", "Client"), ("realtor", "Realtor")], default="client", max_length=20)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("city", models.CharField(blank=True, max_length=80)),
                ("bio", models.TextField(blank=True)),
                ("years_experience", models.PositiveSmallIntegerField(default=0)),
                ("is_verified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Property",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(blank=True, max_length=205, unique=True)),
                ("description", models.TextField()),
                ("property_type", models.CharField(choices=[("apartment", "Apartment"), ("house", "House"), ("land", "Land"), ("commercial", "Commercial"), ("short_stay", "Short stay")], default="apartment", max_length=20)),
                ("purpose", models.CharField(choices=[("sale", "For sale"), ("rent", "For rent"), ("lease", "For lease")], default="sale", max_length=10)),
                ("price", models.DecimalField(decimal_places=2, max_digits=16)),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(default="FCT", max_length=100)),
                ("address", models.CharField(blank=True, max_length=250)),
                ("bedrooms", models.PositiveSmallIntegerField(default=0)),
                ("bathrooms", models.PositiveSmallIntegerField(default=0)),
                ("area_sqm", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("image_url", models.URLField(blank=True, help_text="Optional publicly hosted property image URL")),
                ("owner_authorized", models.BooleanField(default=False)),
                ("review_status", models.CharField(choices=[("pending", "Pending review"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="properties", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Enquiry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("property", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enquiries", to="marketplace.property")),
                ("sender", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="RealtorApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField()),
                ("years_experience", models.PositiveSmallIntegerField(default=0)),
                ("licence_or_company", models.CharField(blank=True, max_length=160)),
                ("status", models.CharField(choices=[("pending", "Pending review"), ("approved", "Approved"), ("declined", "Declined")], default="pending", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="realtor_applications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="SavedProperty",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("property", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="marketplace.property")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="savedproperty",
            constraint=models.UniqueConstraint(fields=("user", "property"), name="unique_saved_property"),
        ),
        migrations.CreateModel(
            name="ViewingRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=40)),
                ("preferred_date", models.DateField()),
                ("message", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="pending", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("property", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="viewing_requests", to="marketplace.property")),
                ("requester", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
