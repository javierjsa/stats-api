import os
import pandas as pd
from statsapi.api.models import ChannelType
from typing import Optional, Union


class StatsManager:

    DATA = None

    def __init__(self):

        base_dir = os.path.dirname(os.path.dirname(__file__))
        full_path = os.path.join(base_dir, "resources/11.parquet")
        if StatsManager.DATA is None:
            print("loaded")
            StatsManager.DATA = pd.read_parquet(full_path, engine='pyarrow')

    def get_channels(self, channel_type: Optional[ChannelType] = None):

        channels = {"velocity": ["vel1", "vel2"],
                    "hummidity": ["humm1", "humm2"],
                    "pressure": ["press1", "press2"],
                    "temperature": ["temp1", "temp2"]}

        if channel_type is None:
            return channels

        else:
            [channels.pop(x) for x in ChannelType if x != channel_type]
            return channels

    def get_stats(self, channels):

        stats = {"vel1": {"mean": "10.0", "std": "2"},
                 "vel2": {"mean": "10.0", "std": "2"},
                 "humm1": {"mean": "10.0", "std": "2"},
                 "humm2": {"mean": "10.0", "std": "2"},
                 "press1": {"mean": "10.0", "std": "2"},
                 "press2": {"mean": "10.0", "std": "2"}}

        [stats.pop(x) for x in list(stats.keys()) if x not in channels]

        return stats
    