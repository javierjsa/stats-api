from enum import Enum
from typing import List, Union, Dict
from pydantic import BaseModel, Field


class ChannelType(str, Enum):
    velocity = "velocity"
    temperature = "temperature"
    humidity = "humidity"
    pressure = "pressure"


class Channels(BaseModel):

    velocity: Union[List[str], None] = Field(default=None, title="Channel ids of type velocity")
    temperature: Union[List[str], None] =  Field(default=None, title="Channel ids of type temperature")
    humidity: Union[List[str], None] = Field(default=None, title="Channel ids of type humidity")
    pressure: Union[List[str], None] = Field(default=None, title="Channel ids of type pressure")

    class Config:
        schema_extra = {
            "example": {
                "velocity": ["vel1", "vel2"],
                "temperature": ["temp1", "temp2"],
                "humidity": ["hum1", "hum2"],
                "pressure": ["press1", "press2"]
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
              "pre1": {"mean": 1500, "std": "250"},
              "tem2": {"mean": 25, "std": 5}
            }
        }
