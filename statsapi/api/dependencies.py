from fastapi import Query
from typing_extensions import Annotated
from typing import FrozenSet
from fastapi.exceptions import HTTPException
from statsapi.api.models import *
from statsapi.stats.stats_manager import StatsManager
from statsapi.stats.utils import StatsManagerException


def get_channels(channel_type: Annotated[Union[ChannelType, None], Query()] = None):

    stats_manager = StatsManager()
    try:
        channels = stats_manager.get_channels(channel_type)
        return Channels(**channels)
    except StatsManagerException as error:
        raise HTTPException(status_code=error.code, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Unexpected error: {str(error)}")


def get_stats(channel_id: Annotated[Union[FrozenSet[str], None], Query()] = None,
              start_date: Annotated[Union[str, None], Query()] = None,
              end_date: Annotated[Union[str, None], Query()] = None):

    stats_manager = StatsManager()
    try:
        stats = stats_manager.get_stats(channel_id, start_date, end_date)
    except StatsManagerException as error:
        raise HTTPException(status_code=error.code, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Unexpected error: {str(error)}")

    for key, val in stats.items():
        stats[key] = Stats(**val)

    channel_stats = ChannelStats()
    channel_stats.data = stats
    return stats
