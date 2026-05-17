import multiprocessing
import time
from unittest import TestCase

from app import create_app, db
from app.config import TestConfig
from app.models import Account

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


localHost = "http://127.0.0.1:5000/"


class AuthSeleniumTests(TestCase):

    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()

        db.create_all()

        self.server_thread = multiprocessing.Process(
            target=self.testApp.run,
            kwargs={
                "host": "127.0.0.1",
                "port": 5000,
                "use_reloader": False
            }
        )
        self.server_thread.daemon = True
        self.server_thread.start()

        time.sleep(1)

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(options=options)

        return super().setUp()

    def tearDown(self):
        if hasattr(self, "driver"):
            self.driver.quit()

        if hasattr(self, "server_thread"):
            self.server_thread.terminate()
            self.server_thread.join()

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        return super().tearDown()

    # Creates an account for Selenium login tests
    def create_account(self, email="test@example.com", password="password123", verified=False):
        account = Account(email=email, is_email_verified=verified)
        account.set_password(password)
        account.generate_friend_code()

        db.session.add(account)
        db.session.commit()

        return account

    # Purpose:
    # Test that clicking the signup tab displays the signup form.
    # Expected:
    # The signup form becomes visible after the signup tab is clicked.
    def test_signup_form_display(self):
        self.driver.get(localHost + "auth")

        AuthPage(self.driver).click_signup_tab()

        signup_form = self.driver.find_element(By.ID, "signup_form")

        self.assertEqual(
            signup_form.value_of_css_property("display"),
            "block",
            "Signup form display failed: signup form should be visible after clicking signup tab."
        )

    # Purpose:
    # Test that invalid signup input does not create an account.
    # Expected:
    # The user remains on the auth page.
    # No account is created in the database.
    def test_invalid_signup(self):
        self.driver.get(localHost + "auth?mode=signup")

        AuthPage(self.driver) \
            .click_signup_tab() \
            .set_signup_email("invalid-email") \
            .set_signup_password("123") \
            .set_signup_confirm_password("123") \
            .submit_signup_form()

        WebDriverWait(self.driver, timeout=10).until(
            EC.url_contains("auth")
        )

        account = Account.query.filter_by(email="invalid-email").first()

        self.assertIn(
            "/auth",
            self.driver.current_url,
            "Invalid signup failed: user should remain on the auth page."
        )

        self.assertIsNone(
            account,
            "Invalid signup failed: invalid signup input should not create an account."
        )

    # Purpose:
    # Test that an unverified user cannot log in through the browser.
    # Expected:
    # The user is redirected to the resend verification page.
    def test_unverified_user_login(self):
        self.create_account(email="unverified@example.com", password="password123", verified=False)

        self.driver.get(localHost + "auth")

        AuthPage(self.driver) \
            .set_login_email("unverified@example.com") \
            .set_login_password("password123") \
            .submit_login_form()

        WebDriverWait(self.driver, timeout=10).until(
            EC.url_contains("mode=resend-verification")
        )

        self.assertIn(
            "mode=resend-verification",
            self.driver.current_url,
            "Unverified login failed: expected redirect URL to contain 'mode=resend-verification', but got '{self.driver.current_url}'."
        )


class AuthPage:

    def __init__(self, driver):
        self.driver = driver

    def click_signup_tab(self):
        self.driver.find_element(By.ID, "signup_btn").click()
        return self

    def click_login_tab(self):
        self.driver.find_element(By.ID, "login_btn").click()
        return self

    def set_login_email(self, email):
        login_form = self.driver.find_element(By.ID, "login_form")
        login_form.find_element(By.NAME, "email").send_keys(email)
        return self

    def set_login_password(self, password):
        login_form = self.driver.find_element(By.ID, "login_form")
        login_form.find_element(By.NAME, "password").send_keys(password)
        return self

    def submit_login_form(self):
        login_form = self.driver.find_element(By.ID, "login_form")
        login_form.find_element(By.ID, "login_submit").click()
        return self

    def set_signup_email(self, email):
        signup_form = self.driver.find_element(By.ID, "signup_form")
        signup_form.find_element(By.NAME, "email").send_keys(email)
        return self

    def set_signup_password(self, password):
        signup_form = self.driver.find_element(By.ID, "signup_form")
        signup_form.find_element(By.NAME, "password").send_keys(password)
        return self

    def set_signup_confirm_password(self, password):
        signup_form = self.driver.find_element(By.ID, "signup_form")
        signup_form.find_element(By.NAME, "confirm_password").send_keys(password)
        return self

    def submit_signup_form(self):
        signup_form = self.driver.find_element(By.ID, "signup_form")
        signup_form.find_element(By.ID, "signup_submit").click()
        return self

