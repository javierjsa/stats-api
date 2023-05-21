from enum import Enum
from typing import List, Union, Dict
from pydantic import BaseModel, Field


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
