from unittest.mock import patch

from app import db
from app.models import Account
from app.tokens import generate_token
from app.tests.test_config import BaseTestCase


class AuthTestCase(BaseTestCase):
    # create a test account
    def create_account(self, email="test@example.com", password="password123", verified=False):
        account = Account(email=email, is_email_verified=verified)
        account.set_password(password)
        account.generate_friend_code()

        db.session.add(account)
        db.session.commit()

        return account

    # replace actual email sending with mock object
    # prevents real SMTP/email calls during testing
    @patch("app.routes.auth.send_email")
    def test_signup_creates_unverified_account(self, mock_send_email):
        response = self.client.post("/signup", data={
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "password123"
        })

        account = Account.query.filter_by(email="new@example.com").first()

        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(account)
        self.assertFalse(account.is_email_verified)
        self.assertTrue(account.check_password("password123"))
        self.assertIsNotNone(account.friend_code)
        mock_send_email.assert_called_once()

    # duplicate email signup should fail
    def test_duplicate_signup_is_rejected(self):
        self.create_account(email="same@example.com")

        response = self.client.post("/signup", data={
            "email": "same@example.com",
            "password": "password123",
            "confirm_password": "password123"
        })

        accounts = Account.query.filter_by(email="same@example.com").all()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(accounts), 1)

    # user should not log in before verifying email
    def test_unverified_user_cannot_login(self):
        self.create_account(
            email="unverified@example.com",
            password="password123",
            verified=False
        )

        response = self.client.post("/login", data={
            "email": "unverified@example.com",
            "password": "password123"
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn("mode=resend-verification", response.location)

    # verification token should verify account
    def test_verify_email_marks_account_as_verified(self):
        account = self.create_account(
            email="verify@example.com",
            verified=False
        )

        token = generate_token(account.email, "verify_email")

        response = self.client.get(f"/verify-email/{token}")

        updated_account = Account.query.filter_by(email="verify@example.com").first()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(updated_account.is_email_verified)

    # password reset should update stored password
    def test_reset_password_changes_password(self):
        account = self.create_account(
            email="reset@example.com",
            password="oldpassword",
            verified=True
        )

        token = generate_token(account.email, "password-reset")

        response = self.client.post(f"/reset-password/{token}", data={
            "password": "newpassword123",
            "confirm_password": "newpassword123"
        })

        updated_account = Account.query.filter_by(email="reset@example.com").first()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(updated_account.check_password("newpassword123"))
        self.assertFalse(updated_account.check_password("oldpassword"))