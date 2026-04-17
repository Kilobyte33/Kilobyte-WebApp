from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from .forms import CustomUserCreationForm, ProfileForm


class ZimbabweAccessTests(TestCase):
    def test_signup_rejects_non_zimbabwe_location(self):
        form = CustomUserCreationForm(
            data={
                "username": "alice",
                "val_email": "alice@example.com",
                "location": "South Africa",
                "password1": "StrongPassword123",
                "password2": "StrongPassword123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("location", form.errors)

    def test_signup_stores_zimbabwe_location(self):
        form = CustomUserCreationForm(
            data={
                "username": "tariro",
                "val_email": "tariro@example.com",
                "location": "zim",
                "password1": "StrongPassword123",
                "password2": "StrongPassword123",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertEqual(user.profile.location, "Zimbabwe")

    def test_profile_form_rejects_non_zimbabwe_location(self):
        user = User.objects.create_user(username="nyasha", password="StrongPassword123")
        form = ProfileForm(
            data={
                "bio": "",
                "phone": "",
                "location": "Botswana",
            },
            instance=user.profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("location", form.errors)

    def test_login_blocks_user_outside_zimbabwe(self):
        user = User.objects.create_user(username="jane", password="StrongPassword123")
        user.profile.location = "Kenya"
        user.profile.save(update_fields=["location"])

        response = self.client.post(
            reverse("login"),
            data={"username": "jane", "password": "StrongPassword123"},
            HTTP_CF_IPCOUNTRY="ZW",
            REMOTE_ADDR="102.177.3.8",
        )

        self.assertContains(
            response,
            "Kilobyte sign in is currently available only to users in Zimbabwe.",
            status_code=200,
        )

    def test_login_allows_user_in_zimbabwe(self):
        user = User.objects.create_user(username="takudzwa", password="StrongPassword123")
        user.profile.location = "Zimbabwe"
        user.profile.save(update_fields=["location"])

        response = self.client.post(
            reverse("login"),
            data={"username": "takudzwa", "password": "StrongPassword123"},
            HTTP_CF_IPCOUNTRY="ZW",
            REMOTE_ADDR="102.177.3.8",
        )

        self.assertEqual(response.status_code, 302)

    @override_settings(DEBUG=False)
    def test_ip_gate_blocks_non_zimbabwe_country_header_on_login(self):
        response = self.client.get(
            reverse("login"),
            HTTP_CF_IPCOUNTRY="ZA",
            REMOTE_ADDR="41.220.1.10",
        )

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Access restricted by location", status_code=403)

    @override_settings(DEBUG=False)
    def test_ip_gate_allows_zimbabwe_country_header_on_signup(self):
        response = self.client.get(
            reverse("signup"),
            HTTP_CF_IPCOUNTRY="ZW",
            REMOTE_ADDR="102.177.3.8",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Account")

    @override_settings(DEBUG=False)
    def test_ip_gate_blocks_missing_country_header_in_production(self):
        response = self.client.get(
            reverse("login"),
            REMOTE_ADDR="102.177.3.8",
        )

        self.assertEqual(response.status_code, 403)

    @override_settings(DEBUG=True)
    def test_ip_gate_allows_local_debug_requests_without_country_header(self):
        response = self.client.get(
            reverse("login"),
            REMOTE_ADDR="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)

    def test_edit_profile_updates_user_and_profile_fields(self):
        user = User.objects.create_user(
            username="oldname",
            email="old@example.com",
            password="StrongPassword123",
        )
        user.profile.phone = "111"
        user.profile.location = "Zimbabwe"
        user.profile.save(update_fields=["phone", "location"])

        self.client.force_login(user)
        response = self.client.post(
            reverse("edit_profile"),
            data={
                "username": "newname",
                "email": "new@example.com",
                "bio": "Updated bio",
                "phone": "222",
                "location": "zim",
            },
        )

        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertEqual(user.username, "newname")
        self.assertEqual(user.email, "new@example.com")
        self.assertEqual(user.profile.bio, "Updated bio")
        self.assertEqual(user.profile.phone, "222")
        self.assertEqual(user.profile.location, "Zimbabwe")
