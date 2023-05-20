from fastapi import APIRouter, Depends
from fastapi import Query, status
from typing_extensions import Annotated
from typing import List, Optional, Union, FrozenSet
from datetime import datetime
from .models import *
from statsapi.api.dependencies import get_channels
from statsapi.stats.stats_manager import StatsManager

router = APIRouter()

@router.get("/channels",
            response_model=Channels,
            status_code=status.HTTP_200_OK,
            response_model_exclude_unset=True,
            summary= "Retrieve available channels names per type",
            response_description="JSON dictionary of channel names sorted by type",
            tags=["List channels"])
async def get_channels(channel_type: Annotated[Union[ChannelType, None], Depends(get_channels)] = None):
    """
    Retrieve available channels per type
    - **channel_type**

    """

    return channel_type


@router.get("/stats", status_code=status.HTTP_200_OK, tags=["Retrieve channel stats"])        
async def get_stats(channel: Annotated[Union[FrozenSet[str], None], Query()] = None,
                    start_date: Annotated[Union[datetime, None], Query()] = None,
                    end_date: Annotated[Union[datetime, None], Query()] = None):
    
    """
    Retrieve stats

    - **channel**: channel list
    - **start_date**:
    - **end_date**:

    """

    stats_manager = StatsManager()
    stats = stats_manager.get_stats(channel, start_date, end_date)
    
    return stats
