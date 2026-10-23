from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Profile, Property, Enquiry, SavedProperty

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

    def test_authorised_submission_waits_for_moderation(self):
        owner = User.objects.create_user(username="seller", password="StrongPassword!2026")
        self.client.force_login(owner)
        response = self.client.post(reverse("property_create"), {
            "title": "Newly Submitted Home",
            "description": "A family home submitted with the owner's authorisation.",
            "property_type": "house",
            "purpose": "sale",
            "price": "45000000",
            "city": "Abuja",
            "state": "FCT",
            "address": "Gwarinpa",
            "bedrooms": "3",
            "bathrooms": "3",
            "area_sqm": "",
            "image_url": "",
            "owner_authorized": "on",
        })
        self.assertEqual(response.status_code, 302)
        prop = Property.objects.get(title="Newly Submitted Home")
        self.assertEqual(prop.review_status, Property.Review.PENDING)
        self.assertTrue(prop.owner_authorized)

    def test_approved_property_accepts_enquiry(self):
        owner = User.objects.create_user(username="seller2", password="StrongPassword!2026")
        prop = Property.objects.create(
            owner=owner, title="Approved Family Home", description="Open plan living",
            price=56000000, city="Abuja", owner_authorized=True,
            review_status=Property.Review.APPROVED,
        )
        response = self.client.post(reverse("send_enquiry", kwargs={"slug": prop.slug}), {
            "name": "Amina Buyer", "email": "amina@example.com",
            "phone": "+2348012345678", "message": "I would like to know more about viewing this home.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Enquiry.objects.filter(property=prop).count(), 1)

    def test_saved_property_can_be_added(self):
        user = User.objects.create_user(username="buyer2", password="StrongPassword!2026")
        owner = User.objects.create_user(username="seller3", password="StrongPassword!2026")
        prop = Property.objects.create(
            owner=owner, title="Approved Starter Home", description="Well situated",
            price=25000000, city="Abuja", owner_authorized=True,
            review_status=Property.Review.APPROVED,
        )
        self.client.force_login(user)
        response = self.client.post(reverse("toggle_saved", kwargs={"slug": prop.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SavedProperty.objects.filter(user=user, property=prop).count(), 1)
