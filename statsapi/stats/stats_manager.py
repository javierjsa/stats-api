import os
import pandas as pd
import numpy as np
from statsapi.api.models import ChannelType
from typing import Union, List, Dict, Any, Tuple
from datetime import datetime
from statsapi.stats.utils import ChannelTypeRegexp, StatsManagerException


class StatsManager:

    DATA = None
    SORTED_CHANNELS = None

    def __init__(self):

        if StatsManager.DATA is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            full_path = os.path.join(base_dir, "resources/11.parquet")
            self.load_data(full_path)

    @classmethod
    def load_data(cls, full_path: os.path) -> None:
        """
        Load available data from file and sort channels per type. Store in class variable

        :param full_path: full parquet file path
        :return: None
        """
        StatsManager.DATA = pd.read_parquet(full_path, engine='pyarrow')
        StatsManager.SORTED_CHANNELS = cls.sort_channels()

    @classmethod
    def sort_channels(cls) -> Dict[str, List[Any]]:
        """
        Sort available channels per channel type, executed when class is instantiated for the first time
        :return: None
        """

        sorted_channels = {}
        for ch in ChannelTypeRegexp:
            data = cls.DATA.filter(regex=f"{ch.value}")
            sorted_channels[ch.name] = list(data.columns)
        return sorted_channels

    @staticmethod
    def get_channels(channel_type: List[ChannelType]) -> Dict[ChannelType, Any]:
        """
        Retrieve channels belonging to a certain channel type
        :param channel_type: enumerated channel type
        :return: Dictionary of lists with channels sorted by type
        """

        if not channel_type:
            return StatsManager.SORTED_CHANNELS

        return {ch.name: StatsManager.SORTED_CHANNELS[ch.value] for ch in channel_type}

    def get_stats(self, channel_ids: Union[List[str], None] = None, start_date: str = None, end_date: str = None):
        """
        Compute mean and standard deviation for a list of channel ids within date range.
        - If no channel identifiers are provided, all channels are used.
        - If no date range provided, full time series is used.
        - If start date provided, but no end date, end date is now.

        :param channel_ids: list of channel identifiers, may be empty
        :param start_date: start date int string format YYYY-m-d, may be empty
        :param end_date: end date int string format YYYY-m-d, may be empty
        :return:
        """

        channel_ids = self.validate_column_names(channel_ids)

        data = self.select_date_range(start_date, end_date)
        data = data[channel_ids]

        mean = data.mean(skipna=True, numeric_only=True)
        std = data.std(skipna=True, numeric_only=True)

        stats = pd.concat([mean, std], axis=1)
        stats.rename(columns={0: "mean", 1: "std"}, inplace=True)
        stats = stats.replace(np.nan, None)
        stats = stats.to_dict('index')
        return stats

    @staticmethod
    def validate_dates(start_date: str = None,
                       end_date: str = None) -> Union[Tuple[datetime, datetime], Tuple[None, None]]:
        """
        Convert date strings to datetime objects. Dates are validated:
        - If no date range provided, None is returned
        - If start date provided, but no end date, end date is now.
        - If validation fails, such as start_date greater than end_date, custom exception is raised

        :param start_date: start date string, may be empty
        :param end_date:  end date string, may be empty
        :return: tuple of datetime object or tuple of None values.
        """

        if isinstance(start_date, datetime) and isinstance(end_date, datetime):
            return start_date, end_date

        if start_date is None and end_date is None:
            return None, None

        if start_date is None and end_date is not None:
            raise StatsManagerException(400, f'Cannot provide end_date without start_date')

        try:
            start_date = datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        except ValueError as error:
            raise StatsManagerException(400, str(error))

        if end_date is None:
            end_date = datetime.now()
        else:
            try:
                end_date = datetime.strptime(f"{end_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
            except ValueError as error:
                raise StatsManagerException(400, str(error))

        if start_date > end_date:
            raise StatsManagerException(400, f"Start_date {start_date} greater than end_date {end_date}")

        return start_date, end_date

    def compute_mean(self, channel_id: str) -> pd.Series:
        """
        Compute mean of channel identifier

        :param channel_id: channel identifier
        :return: pandas series with mean value
        """

        mean = self.DATA[channel_id].mean()
        return mean

    def compute_std(self, channel_id: str) -> pd.Series:
        """
        Compute standard deviation of channel identifier

        :param channel_id: channel identifier
        :return: pandas series with standard deviation value
        """

        std = self.DATA[channel_id].std()
        return std

    def select_date_range(self, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """
        Select date range from available data
        :param start_date: start date datetime object
        :param end_date: end_date datetime object
        :return: pandas dataframe with selected data
        """

        start_date, end_date = self.validate_dates(start_date, end_date)

        if start_date is not None and end_date is not None:
            return self.DATA[(self.DATA.index >= start_date) & (self.DATA.index <= end_date)]

        return self.DATA

    @classmethod
    def validate_column_names(cls, channel_ids: List[str] = None) -> List[str]:
        """
        Check if list of provided channel identifiers is available. If any channel identifier is not available,
        an exception is raised.

        :param channel_ids: list of channel identifiers
        :return: list of verified channel identifiers
        """

        available_cols = list(cls.DATA.columns)

        if not channel_ids:
            return available_cols

        filtered_channels_ids = []

        for ch in channel_ids:
            if ch in available_cols:
                filtered_channels_ids.append(ch)
            else:
                raise StatsManagerException(404, f"Channel_id {ch} is not available")

        return filtered_channels_ids
