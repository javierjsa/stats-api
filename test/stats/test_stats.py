import datetime
import unittest
from unittest.mock import patch
from statsapi.stats.stats_manager import StatsManager
from statsapi.stats.utils import StatsManagerException


class TestStats(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.manager = StatsManager()

    def test_data_loading(self) -> None:
        """
        Assert data is not loaded once a previous StatsManager instance exists
        :return: None
        """

        with patch.object(StatsManager, '_load_data') as mock:
            mock.side_effect = Exception("Attempted to load data")
            _ = StatsManager()

    def test__validate_dates(self) -> None:
        """
        Check valid combinations of start and end dates
        :return: None
        """

        start_date, end_date = self.manager._validate_dates()
        self.assertIsNone(start_date)
        self.assertIsNone(end_date)

        start_date, end_date = self.manager._validate_dates(start_date="2019-05-01")
        self.assertEqual(type(start_date), datetime.datetime)
        self.assertEqual(type(end_date), datetime.datetime)
        now = datetime.datetime.now()
        self.assertEqual(now.date(), end_date.date())
        self.assertTrue(start_date < end_date)

        start_date, end_date = self.manager._validate_dates(start_date="2019-05-01", end_date="2019-07-01")
        self.assertEqual(type(start_date), datetime.datetime)
        self.assertEqual(type(end_date), datetime.datetime)
        self.assertTrue(start_date < end_date)

    def test_fail_date_validation(self) -> None:
        """
        Assert custom exception is raised whenever a malformed date range is provided
        :return: None
        """
        with self.assertRaises(StatsManagerException):
            _, _ = self.manager._validate_dates(end_date="2019-05-01")
        with self.assertRaises(StatsManagerException):
            _, _ = self.manager._validate_dates(start_date="2019-07-01", end_date="2019-05-01")
        with self.assertRaises(StatsManagerException):
            _, _ = self.manager._validate_dates(start_date="20-07-01", end_date="20-05-01")
