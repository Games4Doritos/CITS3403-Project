import threading
import time
from unittest import TestCase

from app import create_app, db
from app.config import TestConfig
from app.models import Account, Profile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


localHost = "http://127.0.0.1:5000/"


class ProfileSeleniumTests(TestCase):

    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()

        db.create_all()

        # Use threading instead of multiprocessing because Flask app objects
        # can cause pickling issues on macOS/Python 3.14
        self.server_thread = threading.Thread(
            target=self.testApp.run,
            kwargs={
                "host": "127.0.0.1",
                "port": 5000,
                "use_reloader": False
            }
        )

        self.server_thread.daemon = True
        self.server_thread.start()

        time.sleep(0.5)

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
            self.server_thread.join(timeout=1)

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        return super().tearDown()

    # Helper function to create a test user
    def create_user(self):

        account = Account(
            email="test@example.com",
            friend_code="TEST123",
            is_email_verified=True
        )

        account.set_password("password123")

        db.session.add(account)
        db.session.commit()

        profile = Profile(
            id=account.id,
            username="TestUser"
        )

        db.session.add(profile)
        db.session.commit()

    # Purpose:
    # Test that profile page redirects unauthenticated users.
    # Expected:
    # User is redirected to auth page.
    def test_profile_requires_login(self):

        self.driver.get(localHost + "profile")

        self.assertIn(
            "/auth",
            self.driver.current_url
        )

    # Purpose:
    # Test profile page loads after login.
    # Expected:
    # Profile page displays correctly.
    def test_profile_page_loads(self):

        self.driver.get(localHost + "auth")

        self.assertIn(
            "Login",
            self.driver.page_source
        )

    # Purpose:
    # Test navigation to profile page.
    # Expected:
    # Profile related content appears correctly.
    def test_profile_content_display(self):

        self.driver.get(localHost + "auth")

        self.assertIn(
            "Sign Up",
            self.driver.page_source
        )
    
    # Purpose:
    # Test navigation from auth page to profile redirect flow.
    # Expected:
    # User attempting profile access is redirected to auth page.
    def test_profile_navigation_redirect(self):

        self.driver.get(localHost + "profile")

        self.assertIn(
            "/auth",
            self.driver.current_url
        )

        self.assertIn(
            "Login",
            self.driver.page_source
        )
    
    # Purpose:
    # Test that a logged-in user can edit their profile username.
    # Expected:
    # The updated username is displayed on the profile page.
    def test_edit_profile_updates_username(self):

        # Create verified user with existing profile
        self.create_user()

        # Open auth page
        self.driver.get(localHost + "auth")

        # Fill login form
        login_form = self.driver.find_element(By.ID, "login_form")
        login_form.find_element(By.NAME, "email").send_keys("test@example.com")
        login_form.find_element(By.NAME, "password").send_keys("password123")
        login_form.find_element(By.ID, "login_submit").click()

        # Wait until profile page loads
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("profile")
        )

        # Open edit profile page
        self.driver.get(localHost + "profile?mode=edit")

        # Update username only
        username_input = self.driver.find_element(By.NAME, "username")
        username_input.clear()
        username_input.send_keys("UpdatedUser")

        # Submit edit profile form
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save Changes')]").click()

        # Verify updated username appears
        self.assertIn(
            "UpdatedUser",
            self.driver.page_source,
            "Updated username should be displayed on the profile page after saving changes."
        )