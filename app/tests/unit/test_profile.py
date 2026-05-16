from app.tests.test_config import BaseTestCase
from app import db
from app.models import Account, Profile


class ProfileTestCase(BaseTestCase):

    # Helper function to create and log in a test user
    def create_logged_in_user(self, with_profile=True):

        # Create test account
        account = Account(
            email="test@example.com",
            friend_code="ABC12345",
            is_email_verified=True
        )

        # Set password for the account
        account.set_password("password123")

        # Save account to test database
        db.session.add(account)
        db.session.commit()

        # Optionally create a profile for the account
        if with_profile:
            profile = Profile(
                id=account.id,
                username="Tester"
            )

            db.session.add(profile)
            db.session.commit()

        # Simulate logged-in session
        with self.client.session_transaction() as session:
            session["_user_id"] = str(account.id)
            session["_fresh"] = True

        return account

    # Test that unauthenticated users are redirected
    def test_profile_requires_login(self):

        response = self.client.get("/profile")

        # 302 means redirect response
        self.assertEqual(response.status_code, 302)

        # Check redirect goes to auth page
        self.assertIn("/auth", response.location)

    # Test that users without profiles are redirected to edit mode
    def test_profile_redirects_to_edit_if_no_profile(self):

        # Create logged-in user without profile
        self.create_logged_in_user(with_profile=False)

        response = self.client.get("/profile")

        self.assertEqual(response.status_code, 302)

        # Check redirect includes edit mode
        self.assertIn("mode=edit", response.location)

    # Test that logged-in users can view their username on profile page
    def test_profile_displays_username_for_logged_in_user(self):

        # Create logged-in user with profile
        self.create_logged_in_user(with_profile=True)

        response = self.client.get("/profile")

        # 200 means successful page load
        self.assertEqual(response.status_code, 200)

        # Check username appears on page
        self.assertIn(b"Tester", response.data)