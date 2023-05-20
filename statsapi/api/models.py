from enum import Enum
from typing import Union, Optional, List
from pydantic import BaseModel

class ChannelType(str, Enum):
    velocity = "velocity"
    temperature = "temperature"
    hummidity = "hummidity"
    pressure = "pressure"

class Channels(BaseModel):

    velocity: Optional[List[str]]
    temperature: Optional[List[str]]
    hummidity: Optional[List[str]]
    pressure: Optional[List[str]]

    class Config:
        schema_extra = {
            "example": {
                "velocity": ["vel1", "vel2"],
                "temperature": ["temp1", "temp2"],
                "hummidity": ["humm1", "humm2"],
                "pressure": ["press1", "press2"]
            }
        }

