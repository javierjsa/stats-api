import unittest
from fastapi import status
from fastapi.testclient import TestClient
from statsapi.api.models import ChannelType
from statsapi.app import app


class TestEndpoints(unittest.TestCase):
    """
    Test api end-to-end
    """

    @classmethod
    def setUpClass(cls):

        cls.client = TestClient(app)
        cls.expected_channels = {'vel': ['vel58.3', 'vel47.5', 'vel32'],
                                 'std': ['std58.3', 'std47.5', 'std32'],
                                 'std_dtr': ['std58.3_detrend', 'std47.5_detrend', 'std32_detrend'],
                                 'temp': ['temp56.8', 'temp10'],
                                 'hum': ['hum56.8'],
                                 'press': ['press56.8'],
                                 'dir': ['dir56.3'],
                                 'sdir': ['sdir56.3']}

        cls.channel_ids = ['vel58.3', 'std58.3', 'std58.3_detrend', 'temp56.8', 'hum56.8', 'press56.8', 'dir56.3',
                           'sdir56.3', 'vel47.5', 'std47.5', 'std47.5_detrend', 'vel32', 'std32', 'std32_detrend',
                           'temp10']

    def test_malformed_channels_requests(self) -> None:
        """
        Assert error is raised if non-existent channel type is requested
        :return: None
        """

        response = self.client.get("/channels?channel_type=foo")
        self.assertEqual(response.json(), {"reason": "Requested invalid channel type"})
        self.assertEqual(response.status_code, 422)

        response = self.client.get(f"/channels?channel_type=velocity&channel_type=humidity")
        self.assertEqual(response.json(), {"reason": "Duplicated channel_type query param: vel, hum"})
        self.assertEqual(response.status_code, 422)

        response = self.client.get(f"/channels?channel_type=velocity&channel_type=velocity")
        self.assertEqual(response.json(),  {"reason":"Duplicated channel_type query param: vel, vel"})
        self.assertEqual(response.status_code, 422)

    def test_request_one_channel_type(self) -> None:
        """
        Request all available channel types, once at a time
        :return: None
        """

        for ch in ChannelType:
            expected_json = {ch.value: self.expected_channels[ch.value]}
            response = self.client.get(f"/channels?channel_type={ch}")
            self.assertEqual(response.status_code, 200)
            received_json = response.json()
            self.assertEqual(received_json, expected_json)

    def test_request_all_channel_types(self) -> None:
        """
        Request all available channels at once
        :return: None
        """

        response = self.client.get(f"/channels")
        received_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_json, self.expected_channels)

    def test_get_stats(self) -> None:
        """
        Retrieve stats for two channels with stat_date and end_date
        :return: None
        """

        channels = ["vel58.3", "std58.3"]
        response = self.client.get(f"/stats?channel_id={channels[0]}&channel_id={channels[1]}"
                                   f"&start_date=2019-05-27&end_date=2019-07-27")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        for ch in channels:
            self.assertTrue(ch in list(data.keys()))
            stats = data[ch]
            for val in ["mean", "std"]:
                self.assertTrue(val in list(stats.keys()))

    def test_get_stats_no_end_date(self) -> None:
        """
        Retrieve stats for two channels with start_date but no end_date
        :return: None
        """

        channels = ["vel58.3", "std58.3"]

        response = self.client.get(f"/stats?channel_id={channels[0]}&channel_id={channels[1]}&start_date=2019-05-27")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for ch in channels:
            self.assertTrue(ch in list(data.keys()))
            stats = data[ch]
            for val in ["mean", "std"]:
                self.assertTrue(val in list(stats.keys()))

    def test_get_stats_no_date(self) -> None:
        """
        Retrieve stats for two channels with no date range
        :return: None
        """

        channels = ["vel58.3", "std58.3"]

        response = self.client.get(f"/stats?channel_id={channels[0]}&channel_id={channels[1]}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for ch in channels:
            self.assertTrue(ch in list(data.keys()))
            stats = data[ch]
            for val in ["mean", "std"]:
                self.assertTrue(val in list(stats.keys()))

    def test_get_stats_all_channels(self) -> None:
        """
        Retrieve stats for all channels within date range
        :return: None
        """
        response = self.client.get(f"/stats?start_date=2019-05-27&end_date=2019-07-27")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for ch in self.channel_ids:
            self.assertTrue(ch in list(data.keys()))
            stats = data[ch]
            for val in ["mean", "std"]:
                self.assertTrue(val in list(stats.keys()))

    def test_get_stats_all_channels_no_date(self) -> None:
        """
        Retrieve stats for all channels for full time series
        :return: None
        """

        response = self.client.get(f"/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for ch in self.channel_ids:
            self.assertTrue(ch in list(data.keys()))
            stats = data[ch]
            for val in ["mean", "std"]:
                self.assertTrue(val in list(stats.keys()))

    def test_get_stat_nonexistent_channel(self) -> None:
        """
        Request stats for non-existent channel
        :return: None
        """

        response = self.client.get(f"/stats?channel_id=foo")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.text, '{"detail":"Channel_id foo is not Available"}')

    def test_get_stats_wrong_time_range(self) -> None:
        """
        Request stats with date range where start_date > end_date
        :return: None
        """

        expected_text = '{"detail":"Start_date 2019-07-27 00:00:00 greater than end_date 2019-05-27 00:00:00"}'
        response = self.client.get(f"/stats?start_date=2019-07-27&end_date=2019-05-27")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.text, expected_text)

    def test_get_stats_no_data(self) -> None:
        """
        Request stats with date range with no data
        :return: None
        """

        response = self.client.get(f"/stats?start_date=1900-05-27&end_date=1900-07-27")
        data = response.json()
        for ch, stats in data.items():
            self.assertTrue(ch in self.channel_ids)
            self.assertIsNone(stats['mean'])
            self.assertIsNone(stats['std'])

