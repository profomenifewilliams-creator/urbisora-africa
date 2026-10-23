from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Profile, Property, ContactMessage, RealtorApplication

User = get_user_model()


class RealtorWorkspaceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agentcv", password="StrongPassword!2026",
            first_name="Ayo", last_name="Danladi", email="agentcv@example.com",
        )
        self.profile = Profile.objects.create(
            user=self.user, role="realtor", city="Abuja",
            professional_title="Residential Property Advisor",
        )
        RealtorApplication.objects.create(user=self.user, message="Realtor", status="approved")

    def test_public_realtor_cv_and_portfolio(self):
        Property.objects.create(
            owner=self.user, title="Portfolio Family Home",
            description="Modern home", price=75000000, city="Abuja",
            owner_authorized=True, review_status=Property.Review.APPROVED,
        )
        response = self.client.get(reverse("realtor_profile", kwargs={"username": self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Portfolio Family Home")
        self.assertContains(response, "Residential Property Advisor")

    def test_profile_editor_saves_professional_fields(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("profile_edit"), {
            "first_name": "Ayo", "last_name": "Danladi", "email": "agentcv@example.com",
            "professional_title": "Property Advisor", "agency_name": "Ayo Homes",
            "phone": "", "city": "Abuja", "bio": "I support clients with residential property.",
            "specialties": "Residential sales, rentals", "languages": "English",
            "service_areas": "Abuja", "website": "", "linkedin_url": "",
            "years_experience": "6",
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.professional_title, "Property Advisor")
        self.assertEqual(self.profile.agency_name, "Ayo Homes")

    def test_contact_form_records_message(self):
        response = self.client.post(reverse("contact"), {
            "full_name": "Ada Example", "email": "ada@example.com",
            "phone": "", "message": "Please contact me about a property.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ContactMessage.objects.filter(email="ada@example.com", status="new").exists())

    def test_only_owner_can_edit_or_archive_a_listing(self):
        listing = Property.objects.create(
            owner=self.user, title="Agent Listing", description="Home",
            price=1000000, city="Abuja", owner_authorized=True,
            review_status=Property.Review.APPROVED,
        )
        stranger = User.objects.create_user(username="stranger", password="StrongPassword!2026")
        self.client.force_login(stranger)
        self.assertEqual(self.client.get(reverse("property_edit", kwargs={"slug": listing.slug})).status_code, 404)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("property_edit", kwargs={"slug": listing.slug})).status_code, 200)
        self.assertEqual(self.client.post(reverse("property_archive", kwargs={"slug": listing.slug})).status_code, 302)
        listing.refresh_from_db()
        self.assertTrue(listing.is_archived)
