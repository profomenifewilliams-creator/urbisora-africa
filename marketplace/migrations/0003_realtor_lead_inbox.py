from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0002_realtor_workspace_and_contact"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="RealtorLead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("message", models.TextField()),
                ("status", models.CharField(choices=[("new", "New"), ("contacted", "Contacted"), ("closed", "Closed")], default="new", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("realtor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="received_realtor_leads", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
