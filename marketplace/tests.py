from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Profile, Property

User = get_user_model()

class MarketplaceSmokeTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
    def test_health_endpoint(self):
        response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
    def test_registration_activates_without_email(self):
        response = self.client.post(reverse("register"), {
            "username": "samplebuyer", "first_name": "Sample", "last_name": "Buyer",
            "email": "sample@example.com", "role": "client", "password1": "StrongPassword!2026",
            "password2": "StrongPassword!2026", "phone": "", "city": "Abuja",
        })
        self.assertIn(response.status_code, (200, 302))
        user = User.objects.get(username="samplebuyer")
        self.assertTrue(user.is_active)
        self.assertTrue(Profile.objects.filter(user=user, role="client").exists())
    def test_property_listing_requires_moderation(self):
        owner = User.objects.create_user(username="agent", password="StrongPassword!2026")
        prop = Property.objects.create(owner=owner, title="Pending test property", description="Test", price=100000, city="Abuja", owner_authorized=True)
        response = self.client.get(reverse("property_list"))
        self.assertNotContains(response, "Pending test property")
