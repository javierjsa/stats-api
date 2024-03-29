import os
from os.path import dirname, abspath
from io import BytesIO
import unittest
from unittest.mock import patch
import pandas as pd
from fastapi import status
from fastapi.testclient import TestClient
from botocore.exceptions import ClientError
from statsapi.app import app
from statsapi.stats.stats_manager import StatsManager


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

        parquet_path = os.path.join(dirname(dirname(dirname(abspath(__file__)))), "resources/11.parquet")
        cls.data = pd.read_parquet(parquet_path)

    def test_malformed_channels_requests(self) -> None:
        """
        Assert error is raised if non-existent channel type is requested
        :return: None
        """
        file_id = "9c750d0955a60f00557b488b713f9320"
        response = self.client.get(f"/channels/{file_id}?channel_type=foo",
                                        headers={'Content-Type': 'application/json'})
        self.assertEqual(response.json(), {'reason': 'Requested invalid channel type: foo'})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_request_one_channel_type(self) -> None:
        """
        Request all available channel types, once at a time
        :return: None
        """

        with patch.object(StatsManager, '_load_data') as mock_method:
            mock_method.return_value = self.data
            expected_json = {"vel": self.expected_channels["vel"]}
            file_id = "9c750d0955a60f00557b488b713f9320"
            response = self.client.get(f"/channels/{file_id}?channel_type=vel",
                                        headers={'Content-Type': 'application/json'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            received_json = response.json()
            self.assertEqual(received_json, expected_json)

            expected_json = {"std_dtr": self.expected_channels["std_dtr"]}
            response = self.client.get(f"/channels/{file_id}?channel_type=std_dtr",
                                        headers={'Content-Type': 'application/json'})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            received_json = response.json()
            self.assertEqual(received_json, expected_json)

    def test_request_duplicated_channel_type(self) -> None:
        """
        Include the same channel type in request twice. Data is filtered by validator
        :return: None
        """

        with patch.object(StatsManager, '_load_data') as mock_method:
            mock_method.return_value = self.data
            file_id = "9c750d0955a60f00557b488b713f9320"
            channel_list = ["vel", "vel"]
            expected_json = {"vel": self.expected_channels["vel"]}
            response = self.client.get(f"/channels/{file_id}?channel_type={channel_list[0]}&channel_type={channel_list[1]}",
                                        headers={'Content-Type': 'application/json'})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            received_json = response.json()
            self.assertEqual(received_json, expected_json)

    def test_request_all_channel_types(self) -> None:
        """
        Request all available channels at once
        :return: None
        """

        with patch.object(StatsManager, '_load_data') as mock_method:
            mock_method.return_value = self.data
            response = self.client.get("/channels/9c750d0955a60f00557b488b713f9320",
                                        headers={'Content-Type': 'application/json'})

            received_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(received_json, self.expected_channels)

    def test_get_stats(self) -> None:
        """
        Retrieve stats for two channels with stat_date and end_date
        :return: None
        """

        with patch.object(StatsManager, '_load_data') as mock_method:
            mock_method.return_value = self.data
            file_id = "9c750d0955a60f00557b488b713f9320"
            channel_ids = ["vel58.3", "std58.3"]
            date_range = ["2019-05-27", "2019-07-27"]

            response = self.client.get(f"/stats/{file_id}?channel_id={channel_ids[0]}&channel_id={channel_ids[1]}",
                                        headers={'Content-Type': 'application/json'})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            for ch in channel_ids:
                self.assertTrue(ch in list(data.keys()))
                stats = data[ch]
                for val in ["mean", "std"]:
                    self.assertTrue(val in list(stats.keys()))

    def test_get_stats_no_end_date(self) -> None:
        """
        Retrieve stats for two channels with start_date but no end_date
        :return: None
        """

        with patch.object(StatsManager, '_load_data') as mock_method:
            mock_method.return_value = self.data
            file_id =  "9c750d0955a60f00557b488b713f9320"
            channels = ["vel58.3", "std58.3"]
            date_range =  ["2019-05-27"]

            response = self.client.get(f"/stats/file_id={file_id}?start_date={date_range[0]}",
                                        headers={'Content-Type': 'application/json'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
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

        file_id = "9c750d0955a60f00557b488b713f9320"
        channel_ids = ["vel58.3", "std58.3"]

        with patch.object(StatsManager, '_load_data') as mock_method:
            mock_method.return_value = self.data
            response = self.client.get(f"/stats/{file_id}?channel_id={channel_ids[0]}&channel_id={channel_ids[1]}",
                                        headers={'Content-Type': 'application/json'})

            self.assertEqual(response.status_code, 200)
            data = response.json()
            for ch in channel_ids:
                self.assertTrue(ch in list(data.keys()))
                stats = data[ch]
                for val in ["mean", "std"]:
                    self.assertTrue(val in list(stats.keys()))

    def test_get_stats_all_channels(self) -> None:
        """
        Retrieve stats for all channels within date range
        :return: None
        """

        file_id = "9c750d0955a60f00557b488b713f9320"
        date_range = ["2019-05-27", "2019-07-27"]

        with patch.object(StatsManager, '_load_data') as mock_method:
            mock_method.return_value = self.data
            response = self.client.get(f"/stats/file_id={file_id}?start_date={date_range[0]}&end_date={date_range[1]}",
                                        headers={'Content-Type': 'application/json'})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
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

        with patch.object(StatsManager, '_load_data') as mock_method:
            mock_method.return_value = self.data
            response = self.client.get(f"/stats/9c750d0955a60f00557b488b713f9320",
                                        headers={'Content-Type': 'application/json'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            for ch in self.channel_ids:
                self.assertTrue(ch in list(data.keys()))
                stats = data[ch]
                for val in ["mean", "std"]:
                    self.assertTrue(val in list(stats.keys()))

    def test_get_stats_nonexistent_channel(self) -> None:
        """
        Request stats for non-existent channel
        :return: None
        """

        file_id = "9c750d0955a60f00557b488b713f9320"
        channel_ids = ["vel58.3", "foo"]


        with patch.object(StatsManager, '_load_data') as mock_method:
            mock_method.return_value = self.data
            response = self.client.get(f"/stats/{file_id}?channel_id={channel_ids[0]}&channel_id={channel_ids[1]}",
                                        headers={'Content-Type': 'application/json'})
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.text, '{"reason":"Channel_id foo is not available"}')

    def test_get_stats_start_date_greater_than_end_date(self) -> None:
        """
        Request stats with date range where start_date > end_date
        :return: None
        """

        file_id = "9c750d0955a60f00557b488b713f9320"
        channel_ids = ["vel58.3", "std58.3"]
        date_range = ["2019-07-27", "2019-05-27"]


        expected_text = '{"reason":"Start_date 2019-07-27 00:00:00 greater than end_date 2019-05-27 00:00:00"}'
        response = self.client.get(f"/stats/{file_id}?channel_id={channel_ids[0]}&channel_id={channel_ids[1]}&start_date={date_range[0]}&end_date={date_range[1]}",
                                        headers={'Content-Type': 'application/json'})

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.text, expected_text)


    def test_get_stats_malformed_start_date(self) -> None:
        """
        Request stats with date range including more than two date strings
        :return: None
        """

        file_id = "9c750d0955a60f00557b488b713f9320"
        channel_ids = ["vel58.3", "std58.3"]
        date_range = ["2019-07", "2019-07-01"]

        expected_text = '{"reason":"Invalid start_date: 2019-07"}'
        response = self.client.get(f"/stats/{file_id}?channel_id={channel_ids[0]}&channel_id={channel_ids[1]}&start_date={date_range[0]}&end_date={date_range[1]}",
                                        headers={'Content-Type': 'application/json'})


        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.text, expected_text)

    def test_get_stats_malformed_end_date(self) -> None:
        """
        Request stats with date range including more than two date strings
        :return: None
        """

        file_id = "9c750d0955a60f00557b488b713f9320"
        channel_ids = ["vel58.3", "std58.3"]
        date_range = ["2019-07-01", "2019-07"]

        expected_text = '{"reason":"Invalid end_date: 2019-07"}'
        response = self.client.get(f"/stats/{file_id}?channel_id={channel_ids[0]}&channel_id={channel_ids[1]}&start_date={date_range[0]}&end_date={date_range[1]}",
                                        headers={'Content-Type': 'application/json'})

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.text, expected_text)

    def test_get_stats_no_data(self) -> None:
        """
        Request stats with date range with no data
        :return: None
        """

        with patch.object(StatsManager, '_load_data') as mock_method:
            mock_method.return_value = self.data

            file_id = "9c750d0955a60f00557b488b713f9320"
            channel_ids = ["vel58.3", "std58.3"]
            date_range = ["1900-05-27", "1900-05-27"]

            response = self.client.get(f"/stats/{file_id}?channel_id={channel_ids[0]}&channel_id={channel_ids[1]}&start_date={date_range[0]}&end_date={date_range[1]}",
                                        headers={'Content-Type': 'application/json'})
            data = response.json()
            for ch, stats in data.items():
                self.assertTrue(ch in self.channel_ids)
                self.assertIsNone(stats['mean'])
                self.assertIsNone(stats['std'])

