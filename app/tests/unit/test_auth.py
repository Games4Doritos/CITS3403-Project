from unittest.mock import patch

from app import db
from app.models import Account
from app.tokens import generate_token
from app.tests.test_config import BaseTestCase


class AuthTestCase(BaseTestCase):
    
    # Creates an account for tests
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
    
    # Purpose:
    # Test that a valid signup creates a new account.
    # Expected:
    # The account is saved in the database.
    # The account is not email-verified yet.
    # A verification email is triggered exactly once.
    def test_signup_creates_unverified_account(self, mock_send_email):
        response = self.client.post(
            "/signup",
            data={
                "email": "new@example.com",
                "password": "password123",
                "confirm_password": "password123"
            }
        )

        account = Account.query.filter_by(email="new@example.com").first()

        self.assertIsNotNone(account, "Signup failed: account was not created.")
        self.assertFalse(account.is_email_verified, "Signup failed: new account should not be verified yet.")
        self.assertTrue(account.check_password("password123"), "Signup failed: password was not stored correctly.")
        self.assertIsNotNone(account.friend_code, "Signup failed: friend code was not generated.")
        self.assertEqual(response.status_code, 302, "Signup failed: successful signup should redirect.")
        self.assertEqual(mock_send_email.call_count, 1, "Signup failed: verification email should be sent exactly once.")

    
    # Purpose:
    # Test that signup rejects an email already used by another account.
    # Expected:
    # No duplicate account is created.
    # The route redirects back to the signup/auth page.
    def test_duplicate_signup_is_rejected(self):
        self.create_account(email="same@example.com")
        response = self.client.post(
            "/signup",
            data={
                "email": "same@example.com",
                "password": "password123",
                "confirm_password": "password123"
            }
        )

        accounts = Account.query.filter_by(email="same@example.com").all()

        self.assertEqual(len(accounts), 1, "Duplicate signup failed: duplicate account was created.")
        self.assertEqual(response.status_code, 302, "Duplicate signup failed: route should redirect after rejection.")

    
    # Purpose:
    # Test that an unverified user cannot log in.
    # Expected:
    # The user is redirected to the resend verification page.
    def test_unverified_user_cannot_login(self):
        self.create_account(email="unverified@example.com", password="password123",verified=False)

        response = self.client.post(
            "/login",
            data={
                "email": "unverified@example.com",
                "password": "password123"
            }
        )

        self.assertEqual(response.status_code, 302, "Unverified login failed: login attempt should redirect.")
        self.assertIn("mode=resend-verification", response.location, "Unverified login failed: user should be redirected to resend verification page.")

    
    # Purpose:
    # Test that a valid email verification token verifies the account.
    # Expected:
    # The account's is_email_verified value becomes True.
    def test_verify_email_marks_account_as_verified(self):
        account = self.create_account(email="verify@example.com", verified=False)

        token = generate_token(account.email, "verify_email")

        response = self.client.get(f"/verify-email/{token}")

        updated_account = Account.query.filter_by(email="verify@example.com").first()

        self.assertTrue(updated_account.is_email_verified, "Email verification failed: account should be marked as verified.")
        self.assertEqual(response.status_code, 302, "Email verification failed: route should redirect after successful verification.")

    
    # Purpose:
    # Test that password reset with a valid token updates the account password.
    # Expected:
    # The old password no longer works.
    # The new password works.
    def test_reset_password_changes_password(self):
        account = self.create_account(email="reset@example.com", password="oldpassword", verified=True)

        token = generate_token(account.email, "password-reset")

        response = self.client.post(
            f"/reset-password/{token}",
            data={
                "password": "newpassword123",
                "confirm_password": "newpassword123"
            }
        )

        updated_account = Account.query.filter_by(email="reset@example.com").first()

        self.assertFalse(updated_account.check_password("oldpassword"), "Password reset failed: old password should no longer work.")   
        self.assertTrue(updated_account.check_password("newpassword123"), "Password reset failed: new password should work.")
        self.assertEqual(response.status_code, 302, "Password reset failed: route should redirect after successful reset.")