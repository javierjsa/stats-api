from enum import Enum
from typing import List, Union, Dict
from pydantic import BaseModel, Field, validator
from fastapi.exceptions import HTTPException
from fastapi import status
from datetime import datetime


class ChannelType(Enum):
    vel = "vel"
    std = "std"
    std_dtr = "std_dtr"
    temp = "temp"
    hum = "hum"
    press = "press"
    dir = "dir"
    sdir = "sdir"


class Channels(BaseModel):

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

    mean: Union[float, None] = Field(default=None, title="channel mean")
    std: Union[float, None] = Field(default=None, title="channel standard deviation")

    class Config:
        schema_extra = {
            "example": {
                "mean": 10.0,
                "std": 2.5
            }
        }


class ChannelStats(BaseModel):

    data: Dict[str, Union[str, Dict[str, Stats]]] = Field(default=None, title="Nested dictionary of channel stats")

    class Config:
        schema_extra = {
            "example": {
              "vel1": {"mean": 10.0, "std": "2.5"},
              "press1": {"mean": 1500, "std": "250"},
              "temp2": {"mean": 25, "std": 5}
            }
        }


class ChannelRequest(BaseModel):

    channel_type: Union[List[ChannelType], None] = []

    class Config:
        schema_extra = {
            "example": {
              "channel_type": ["vel", "temp"]
            }
        }

    @validator('channel_type', pre=True, always=False)
    def check_channel_type(cls, channel_type):

        channel_type = list(set(channel_type))

        for ch in channel_type:
            if ch not in [cha.value for cha in ChannelType]:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail={"reason": f"Requested invalid channel type: {ch}"})

        return channel_type


class StatsRequest(BaseModel):

    channel_ids: Union[List[str], None] = []
    date_range: List[Union[str, None]] = [None, None]

    class Config:
        schema_extra = {
            "example": {
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
                                detail={'reason': f'Malformed date range, length larger than two'})

        start_date = date_range[0]
        try:
            end_date = date_range[1]
        except IndexError:
            end_date = None

        if start_date is None and end_date is None:
            return start_date, end_date

        if start_date is None and end_date is not None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail={'reason': f'Cannot provide end_date without start_date'})

        if end_date is not None:
            try:
                end_date = datetime.strptime(f"{end_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
            except ValueError as _:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail={'reason': f'Invalid end_date: {end_date}'})
        else:
            end_date = datetime.now()

        try:
            start_date = datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        except ValueError as _:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail={'reason': f'Invalid start_date: {start_date}'})

        if start_date > end_date:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail={'reason': f"Start_date {start_date} greater than end_date {end_date}"})

        return start_date, end_date

