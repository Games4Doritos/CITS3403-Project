import unittest

from app import create_app, db
from app.config import TestConfig

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        db.create_all()

        # allow to simulate requests
        self.client = self.testApp.test_client() 

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
