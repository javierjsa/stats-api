import unittest
from fastapi.testclient import TestClient
from statsapi.api.models import ChannelType, Channels, ChannelStats
from typing import Optional, List, FrozenSet, Union
from statsapi.api.dependencies import get_channels
from statsapi.app import app
from copy import deepcopy

def mock_get_channels(channel_type: Optional[ChannelType] = None):
    channels = {"velocity": ["vel1", "vel2"],
                "humidity": ["hum1", "hum2"],
                "pressure": ["pre1", "pre2"],
                "temperature": ["tem1", "tem2"]}

    if channel_type is not None:
        [channels.pop(x) for x in ChannelType if x != channel_type]

    return Channels(**channels)


def mock_get_stats(channel_id: Optional[List[str]] = None):

    stats = {"vel1": {"mean": 10.0, "std": "2.5"},
             "vel2": {"mean": 10.0, "std": "2.5"},
             "pre1": {"mean": 1500, "std": "250"},
             "pre2": {"mean": 1500, "std": "250"},
             "tem1": {"mean": 25, "std": 5},
             "tem2": {"mean": 25, "std": 5}}
    if channel_id is not None:
        stats = {key: val for key,val in stats.items() if key in channel_id}

    return ChannelStats(**stats)


class TestEndpoints(unittest.TestCase):
    """
    Test api endpoints. Dependencies are mocked
    """

    @classmethod
    def setUpClass(cls):

        app.dependency_overrides[get_channels] = mock_get_channels
        cls.client = TestClient(app)

    def test_malformed_requests(self):
        """
        Assert error is raised if non-existent channel type is requested
        """

        response = self.client.get("/channels?channel_type=foo")
        self.assertEqual(response.status_code, 422)

        response = self.client.get(f"/channels?channel_type=velocity&channel_type=humidity")
        self.assertEqual(response.status_code, 422)

        response = self.client.get(f"/channels?channel_type=velocity&channel_type=velocity")
        self.assertEqual(response.status_code, 422)

    def test_request_one_channel_type(self):
        """
        Request all available channel types, once at a time
        """

        for ch in ChannelType:
            channel = str(ch.value)
            expected_json = {channel: [f"{channel[:3]}1", f"{channel[:3]}2"]}
            response = self.client.get(f"/channels?channel_type={ch}")
            received_json = response.json()
            self.assertEqual(received_json, expected_json)

    def test_request_all_channel_types(self):
        """
        Request all available channels all at once
        """

        expected_json = {"velocity": ["vel1", "vel2"],
                         "humidity": ["hum1", "hum2"],
                         "pressure": ["pre1", "pre2"],
                         "temperature": ["tem1", "tem2"]}

        response = self.client.get(f"/channels")
        received_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_json, expected_json)





