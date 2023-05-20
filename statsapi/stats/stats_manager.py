import os
import pandas as pd
import numpy as np
from statsapi.api.models import ChannelType
from typing import Optional, Union, List
from datetime import datetime
from statsapi.stats.utils import ChannelTypeRegexp, StatsManagerException


class StatsManager:

    DATA = None
    SORTED_CHANNELS = None

    def __init__(self):

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        full_path = os.path.join(base_dir, "resources/11.parquet")
        if StatsManager.DATA is None:
            StatsManager.DATA = pd.read_parquet(full_path, engine='pyarrow')
            StatsManager.SORTED_CHANNELS = self.sort_channels()

    @classmethod
    def sort_channels(cls):

        sorted_channels = {}
        for ch in ChannelTypeRegexp:
            data = cls.DATA.filter(regex=f"{ch.value}")
            sorted_channels[ch.name] = list(data.columns)
        return sorted_channels

    def get_channels(self, channel_type):

        if channel_type is None:
            return StatsManager.SORTED_CHANNELS

        return {channel_type: StatsManager.SORTED_CHANNELS[channel_type]}

    def get_stats(self, channel_ids, start_date, end_date):

        channel_ids = self.validate_column_names(channel_ids)

        data = self.select_date_range(start_date, end_date)
        data = data[channel_ids]

        mean = data.mean()
        std = data.std()

        stats = pd.concat([mean, std], axis=1)
        stats.rename(columns={0: "mean", 1: "std"}, inplace=True)
        stats = stats.replace(np.nan, None)
        stats = stats.to_dict('index')
        return stats

    def validate_dates(self, start_date, end_date):

        if start_date is None and end_date is None:
            return None, None

        if start_date is None and end_date is not None:
            raise StatsManagerException(400, "Null start_date is not allowed when end_date is provided")

        start_date = datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S")

        if end_date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(f"{end_date} 00:00:00", "%Y-%m-%d %H:%M:%S")

        if start_date > end_date:
            raise StatsManagerException(400, f"Start_date {start_date} greater than end_date {end_date}")


        return start_date, end_date

    def compute_mean(self, channel_id):

        mean = self.DATA[channel_id].mean()
        return mean

    def select_date_range(self, start_date, end_date):

        start_date, end_date = self.validate_dates(start_date, end_date)

        if start_date is not None and end_date is not None:
            return self.DATA[(self.DATA.index >= start_date) & (self.DATA.index <= end_date)]

        return self.DATA

    def compute_std(self, channel_id):

        std = self.DATA[channel_id].std()
        return std

    @classmethod
    def validate_column_names(cls, channel_ids: List[str] = None):

        available_cols = list(cls.DATA.columns)

        if channel_ids is None:
            return available_cols

        filtered_channels_ids = []

        for ch in channel_ids:
            if ch in available_cols:
                filtered_channels_ids.append(ch)
            else:
                raise StatsManagerException(404, f"Channel_id {ch} is not Available")

        return filtered_channels_ids
