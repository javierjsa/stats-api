from typing import Dict, Union
from io import BytesIO
from typing_extensions import Annotated
from fastapi import APIRouter, status, File
from fastapi.exceptions import HTTPException
from statsapi.api.models import (ChannelRequest, Channels,
                                 StatsRequest, Stats, FileId)
from statsapi.stats.stats_manager import StatsManager
from statsapi.stats.utils import StatsManagerException


router = APIRouter()


@router.post("/channels",
             response_model=Channels,
             status_code=status.HTTP_200_OK,
             response_model_exclude_unset=True,
             summary="Retrieve available channels identifiers per type",
             response_description="JSON dictionary of channel names sorted by type",
             tags=["List channels"])
async def get_channels(channel_request: Union[ChannelRequest, None]):
    """
    ### Retrieve available channel identifiers per type.<br/>
    - ### Allowed channel types are: vel, std, std_dtr, temp, hum, press, dir, sdir.<br/>
    - ### Requesting a channels type outside allowed values will raise an error.
    - ### Duplicated channel types are filtered before processing.

    ### Receives: _ChannelRequest_ model with optional list of channel_type values.<br/>
    ### Returns: _Channels_ model with dictionary of available channels sorted by channel type.
    """

    stats_manager = StatsManager()
    try:
        channels = stats_manager.get_channels(channel_request.file_id,
                                              list(channel_request.channel_list))
        return Channels(**channels)
    except StatsManagerException as error:
        raise HTTPException(status_code=error.code, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Unexpected error: {str(error)}")


@router.post("/stats", status_code=status.HTTP_200_OK,
             summary="Retrieve stats for provided channel identifiers within date range",
             response_description="JSON dictionary of channel names sorted by type",
             tags=["Retrieve channel stats"])
async def get_channel_stats(stats_request: Union[StatsRequest, None]) -> Dict[str, Stats]:
    """
    ### Retrieve stats (mean and standard deviation) for requested channel identifiers.

    - ### In case no channel is specified, stats for all channels are returned.
    - ### A date range may be provided, otherwise stats are computed for the whole time series.
    - ### Should only start_date is specified, end_date is set to now.
    - ### Providing any nonexistent channel identifiers will raise an error

    ### Receives: _StatsRequest_ model including an optional list of channels and
    ### an optional date range.<br/>
    ### Returns:  Dictionary of _Stats_ models including dictionary of dictionaries
    ### with stats sorted by channel.
    """

    stats_manager = StatsManager()
    try:
        data = stats_request.dict()
        stats = stats_manager.get_stats(file_id=data['file_id'],
                                        channel_ids=data['channel_ids'],
                                        start_date=data['date_range'][0],
                                        end_date=data['date_range'][1])
    except StatsManagerException as error:
        raise HTTPException(status_code=error.code, detail={"reason": str(error)})
    except Exception:
        import traceback
        raise HTTPException(status_code=503,
                            detail={"reason": f"Unexpected error: {traceback.format_exc()}"})

    for key, val in stats.items():
        stats[key] = Stats(**val)

    return stats


@router.post("/upload", status_code=status.HTTP_200_OK,
             summary="Upload parquet file",
             response_description="File id in db",
             tags=["Thumbnail"])
async def upload_file(file: Annotated[bytes, File()]) -> FileId:
    """
    Upload file to storage. Return file id and path
    """

    stats_manager = StatsManager()
    try:
        data = BytesIO(file)
        file_id = stats_manager.store_data(data)
        return FileId(id=file_id, path="/aa")
    except Exception as e:
        return FileId(id="error", path=f"{e}")
