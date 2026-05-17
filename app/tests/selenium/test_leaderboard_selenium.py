import threading # Use threading instead of multiprocessing to avoid Flask app pickling issues on macOS/Python 3.14
import time
from unittest import TestCase

from app import create_app, db
from app.config import TestConfig
from app.models import Account, Profile, BestStats

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


localHost = "http://127.0.0.1:5000/"


class LeaderboardSeleniumTests(TestCase):

    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()

        db.create_all()

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
            
            self.server_thread.join(timeout=1) # lets the thread clean up properly,prevents leftover background threads

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        return super().tearDown()

    # Helper function to create leaderboard players
    def create_player(self, email, username, score):

        account = Account(
            email=email,
            friend_code=username[:8].upper(),
            is_email_verified=True
        )

        account.set_password("password123")

        db.session.add(account)
        db.session.commit()

        profile = Profile(
            id=account.id,
            username=username
        )

        stats = BestStats(
            id=account.id,
            highscore=score,
            longest_time=10.0,
            jump_count=5,
            currency=0,
            total_games=1
        )

        db.session.add(profile)
        db.session.add(stats)
        db.session.commit()

    # Purpose:
    # Test that leaderboard page opens successfully.
    # Expected:
    # The page loads and displays the leaderboard heading.
    def test_leaderboard_page_loads(self):

        self.driver.get(localHost + "leaderboard")

        self.assertIn(
            "Leaderboard",
            self.driver.page_source
        )

    # Purpose:
    # Test that leaderboard displays player username and score.
    # Expected:
    # Player username and score appear on the page.
    def test_leaderboard_displays_player_score(self):

        self.create_player(
            email="player@example.com",
            username="PlayerOne",
            score=500
        )

        self.driver.get(localHost + "leaderboard")

        self.assertIn(
            "PlayerOne",
            self.driver.page_source
        )

        self.assertIn(
            "500",
            self.driver.page_source
        )

    # Purpose:
    # Test leaderboard ranking order.
    # Expected:
    # Higher score player appears before lower score player.
    def test_leaderboard_ranking_order(self):

        self.create_player(
            email="low@example.com",
            username="LowScore",
            score=100
        )

        self.create_player(
            email="high@example.com",
            username="HighScore",
            score=900
        )

        self.driver.get(localHost + "leaderboard")

        page_source = self.driver.page_source

        self.assertLess(
            page_source.index("HighScore"),
            page_source.index("LowScore")
        )
    
    # Purpose:
    # Test navigation from home page to leaderboard page.
    # Expected:
    # Clicking the Leaderboard link opens the leaderboard page.
    def test_home_to_leaderboard_navigation(self):

        self.driver.get(localHost)

        self.driver.find_element(By.LINK_TEXT, "Leaderboard").click()

        self.assertIn(
            "/leaderboard",
            self.driver.current_url
        )

        self.assertIn(
            "Leaderboard",
            self.driver.page_source
        )

    # Purpose:
    # Test game navigation from leaderboard page.
    # Expected:
    # Clicking Play Now opens the game page.
    def test_leaderboard_start_playing_navigation(self):

        self.driver.get(localHost + "leaderboard")

        self.driver.find_element(By.LINK_TEXT, "Play Now!").click()

        self.assertIn(
            "/play",
            self.driver.current_url
        )
