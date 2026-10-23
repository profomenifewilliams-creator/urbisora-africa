from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("marketplace", "0001_initial")]
    operations = [
        migrations.AddField(model_name="profile", name="photo", field=models.ImageField(blank=True, upload_to="realtor_profiles/")),
        migrations.AddField(model_name="profile", name="professional_title", field=models.CharField(default="Real Estate Professional", max_length=160)),
        migrations.AddField(model_name="profile", name="agency_name", field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name="profile", name="show_phone", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="profile", name="show_email", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="profile", name="specialties", field=models.CharField(blank=True, help_text="Separate specialties with commas.", max_length=300)),
        migrations.AddField(model_name="profile", name="languages", field=models.CharField(blank=True, help_text="Languages you can work in.", max_length=200)),
        migrations.AddField(model_name="profile", name="service_areas", field=models.CharField(blank=True, help_text="Cities, districts or states you cover.", max_length=240)),
        migrations.AddField(model_name="profile", name="website", field=models.URLField(blank=True)),
        migrations.AddField(model_name="profile", name="linkedin_url", field=models.URLField(blank=True)),
        migrations.AddField(model_name="property", name="is_archived", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="enquiry", name="status", field=models.CharField(choices=[("new", "New"), ("contacted", "Contacted"), ("closed", "Closed")], default="new", max_length=12)),
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("message", models.TextField()),
                ("status", models.CharField(choices=[("new", "New"), ("handled", "Handled"), ("closed", "Closed")], default="new", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
