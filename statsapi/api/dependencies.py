from fastapi import APIRouter, Depends
from fastapi import Query, status
from typing_extensions import Annotated
from typing import List, Optional, Union, FrozenSet
from datetime import datetime
from .models import *
from statsapi.stats.stats_manager import StatsManager


def get_channels(channel_type: Annotated[Union[ChannelType, None], Query()] = None):

    stats_manager = StatsManager()
    return Channels(**stats_manager.get_channels(channel_type))


def get_stats(channel: Annotated[Union[FrozenSet[str], None], Query()] = None,
                    start_date: Annotated[Union[datetime, None], Query()] = None,
                    end_date: Annotated[Union[datetime, None], Query()] = None):

    stats_manager = StatsManager()
    return stats_manager.get_stats(channel, start_date, end_date)