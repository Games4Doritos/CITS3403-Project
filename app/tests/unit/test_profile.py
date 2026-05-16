from app.tests.test_config import BaseTestCase


class ProfileTestCase(BaseTestCase):

    def test_profile_requires_login(self):
        response = self.client.get("/profile")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth", response.location)