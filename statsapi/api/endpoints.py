from fastapi import APIRouter
from statsapi.api.models import *
from statsapi.stats.stats_manager import StatsManager
from statsapi.stats.utils import StatsManagerException


router = APIRouter()


@router.post("/channels",
             response_model=Channels,
             status_code=status.HTTP_200_OK,
             response_model_exclude_unset=True,
             summary="Retrieve available channels names per type",
             response_description="JSON dictionary of channel names sorted by type",
             tags=["List channels"])
async def get_channels(channel_type: Union[ChannelRequest, None]):
    """
    Retrieve available channels per type
    - **channel_type**

    """

    stats_manager = StatsManager()
    try:
        channels = stats_manager.get_channels(list(channel_type.channel_list))
        return Channels(**channels)
    except StatsManagerException as error:
        raise HTTPException(status_code=error.code, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Unexpected error: {str(error)}")


@router.post("/stats", status_code=status.HTTP_200_OK, tags=["Retrieve channel stats"])
async def get_stats(stats_request: Union[StatsRequest, None]):
    """
    Retrieve stats

    - **channel**: channel list
    - **start_date**:
    - **end_date**:

    """

    stats_manager = StatsManager()
    try:
        data = stats_request.dict()
        stats = stats_manager.get_stats(channel_ids=data['channel_ids'],
                                        start_date=data['date_range'][0],
                                        end_date=data['date_range'][1])
    except StatsManagerException as error:
        raise HTTPException(status_code=error.code, detail={"reason": str(error)})
    except Exception as error:
        raise HTTPException(status_code=503, detail={"reason": f"Unexpected error: {str(error)}"})

    for key, val in stats.items():
        stats[key] = Stats(**val)

    channel_stats = ChannelStats()
    channel_stats.data = stats
    return stats
