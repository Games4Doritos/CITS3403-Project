from app.tests.test_config import BaseTestCase
from app import db
from app.models import Account, Profile, BestStats


class LeaderboardTestCase(BaseTestCase):

    # Helper function to create a user with score data
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

        return account

    # Test leaderboard page loads successfully
    def test_leaderboard_page_loads(self):
        response = self.client.get("/leaderboard")

        self.assertEqual(response.status_code, 200)

    # Test leaderboard displays player username and score
    def test_leaderboard_displays_player_score(self):
        self.create_player(
            email="player@example.com",
            username="PlayerOne",
            score=500
        )

        response = self.client.get("/leaderboard")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PlayerOne", response.data)
        self.assertIn(b"500", response.data)