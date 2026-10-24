import json
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Enquiry, Profile, Property, RealtorApplication, RealtorLead, SavedProperty

User = get_user_model()


class UrbisoraAgentTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="agentowner", password="StrongPassword!2026",
            first_name="Ada", last_name="Owner", email="owner@example.com",
        )
        Profile.objects.create(user=self.owner, role=Profile.Role.REALTOR, city="Abuja")
        RealtorApplication.objects.create(user=self.owner, message="Approved realtor", status=RealtorApplication.Status.APPROVED)
        self.property = Property.objects.create(
            owner=self.owner, title="Agent Test Family Home", description="Three bedroom family home",
            price=45000000, city="Abuja", state="FCT", bedrooms=3, owner_authorized=True,
            review_status=Property.Review.APPROVED,
        )

    def test_agent_returns_live_property_search_results(self):
        response = self.client.post(
            reverse("ai_chat"),
            data=json.dumps({"message": "Find houses for sale in Abuja", "history": []}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Agent Test Family Home", str(data))
        self.assertTrue(any(card.get("kind") == "property" for card in data.get("cards", [])))

    def test_agent_shows_platform_contact_details(self):
        response = self.client.post(
            reverse("ai_chat"),
            data=json.dumps({"message": "What is your contact phone number?", "history": []}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("+234 906 791 2928", str(response.json()))

    def test_archive_requires_confirmation_and_owner_permission(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("ai_action"),
            data=json.dumps({"type": "archive_property", "object_id": self.property.pk, "confirmed": False}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.property.refresh_from_db()
        self.assertFalse(self.property.is_archived)

        confirmed = self.client.post(
            reverse("ai_action"),
            data=json.dumps({"type": "archive_property", "object_id": self.property.pk, "confirmed": True}),
            content_type="application/json",
        )
        self.assertEqual(confirmed.status_code, 200)
        self.property.refresh_from_db()
        self.assertTrue(self.property.is_archived)

    def test_agent_cannot_archive_another_members_property(self):
        other = User.objects.create_user(username="notowner", password="StrongPassword!2026")
        self.client.force_login(other)
        response = self.client.post(
            reverse("ai_action"),
            data=json.dumps({"type": "archive_property", "object_id": self.property.pk, "confirmed": True}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.property.refresh_from_db()
        self.assertFalse(self.property.is_archived)

    def test_agent_save_property_goes_only_to_signed_in_users_shortlist(self):
        other = User.objects.create_user(username="buyer", password="StrongPassword!2026")
        self.client.force_login(other)
        response = self.client.post(
            reverse("ai_action"),
            data=json.dumps({"type": "save_property", "object_id": self.property.pk, "confirmed": True}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SavedProperty.objects.filter(user=other, property=self.property).exists())
        self.assertFalse(SavedProperty.objects.filter(user=self.owner, property=self.property).exists())

    @override_settings(URBISORA_AI_API_KEY="")
    def test_general_fallback_does_not_require_external_ai_key(self):
        response = self.client.post(
            reverse("ai_chat"),
            data=json.dumps({"message": "Can you explain what makes a good real estate profile?", "history": []}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Urbisora Assistant", response.json()["reply"])
