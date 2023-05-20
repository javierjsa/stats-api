import unittest
import pandas as pd
from fastapi.testclient import TestClient
from statsapi.app import app


class TestApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.client = TestClient(app)

    def setUp(self) -> None:
        return super().setUp()

    def test_wrong_channel_type(self):
        """
        Assert error is raised if non-existent channel type is requested
        """

        response = self.client.get("/channels?channel_type=foo")
        self.assertEqual(response.status_code, 422)



