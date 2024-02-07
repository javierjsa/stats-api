"""
API endpoint models that facilitate handling and validation of request and response data
"""
from enum import Enum
from typing import List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from fastapi.exceptions import HTTPException
from fastapi import status


class FileId(BaseModel):
    """
    File model with fields id and stored. Field stored is true if file was saved to backend,
    false if file alreadt existed
    """

    file_id: str
    stored: bool


class ChannelType(Enum):
    """
    Available channels/columns in parque file
    """
    vel = "vel"
    std = "std"
    std_dtr = "std_dtr"
    temp = "temp"
    hum = "hum"
    press = "press"
    dir = "dir"
    sdir = "sdir"


class Channels(BaseModel):
    """
    Response model for available channel identifier requests
    """

    vel: Union[List[str], None] = Field(default=None, title="Channel ids of type vel")
    std: Union[List[str], None] = Field(default=None, title="Channel ids of type std")
    std_dtr: Union[List[str], None] = Field(default=None, title="Channel ids of type std_dtr")
    temp: Union[List[str], None] = Field(default=None, title="Channel ids of type temp")
    hum: Union[List[str], None] = Field(default=None, title="Channel ids of type hum")
    press: Union[List[str], None] = Field(default=None, title="Channel ids of type press")
    dir: Union[List[str], None] = Field(default=None, title="Channel ids of type dir")
    sdir: Union[List[str], None] = Field(default=None, title="Channel ids of type sdir")

    class Config:
        schema_extra = {
            "example": {
                "vel": ["vel1", "vel2"],
                "temp": ["temp1", "temp2"],
                "hum": ["hum1", "hum2"],
                "press": ["press1", "press2"]
            }
        }


class Stats(BaseModel):
    """
    Response model for channel stats requests
    """

    mean: Union[float, None] = Field(default=None, title="channel mean")
    std: Union[float, None] = Field(default=None, title="channel standard deviation")

    class Config:
        schema_extra = {
            "example": {
                "mean": 10.0,
                "std": 2.5
            }
        }


class ChannelRequest(BaseModel):
    """
    Request model for available channel identifiers
    """

    file_id: str
    channel_list: Union[List[ChannelType], None] = Field(default=[],
                                                         title="List of requested channel types")

    class Config:
        schema_extra = {
            "example": {
                "file_id": "9c750d0955a60f00557b488b713f9320",
                "channel_list": ["vel56.8", "std56.8"]
            }
        }

    @validator('channel_list', pre=True, always=False)
    def check_channel_list(cls, channel_list):

        channel_list = list(set(channel_list))

        for ch in channel_list:
            if ch not in [cha.value for cha in ChannelType]:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail={"reason": f"Requested invalid channel type: {ch}"})

        return channel_list


class StatsRequest(BaseModel):
    """
    Request model for channel stats requests
    """

    file_id: str = Field(title="File identifier")
    channel_ids: Union[List[str], None] = Field(default=[], title="List of channel identifiers")
    date_range: List[Union[str, None]] = Field(default=[None, None], title="Date range string with forma YYYY-m-d")

    class Config:
        schema_extra = {
            "example": {
                "file_id": "9c750d0955a60f00557b488b713f9320",
                "channel_ids": ["vel58.3"],
                "date_range": ["2019-05-01", "2019-07-01"]
            }
        }

    @validator('channel_ids', pre=True, always=False)
    def check_channel_ids(cls, channel_ids):

        return list(set(channel_ids))

    @validator('date_range', pre=False, always=False)
    def check_date_range(cls, date_range):

        if len(date_range) > 2:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail={'reason': 'Malformed date range, length larger than two'})

        start_date = date_range[0]
        try:
            end_date = date_range[1]
        except IndexError:
            end_date = None

        if start_date is None and end_date is None:
            return start_date, end_date

        if start_date is None and end_date is not None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail={'reason': 'Cannot provide end_date without start_date'})

        if end_date is not None:
            try:
                end_date = datetime.strptime(f"{end_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail={'reason': f'Invalid end_date: {end_date}'})
        else:
            end_date = datetime.now()

        try:
            start_date = datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail={'reason': f'Invalid start_date: {start_date}'})

        if start_date > end_date:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail={'reason': f"Start_date {start_date} greater than end_date {end_date}"})

        return start_date, end_date
