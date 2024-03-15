from enum import Enum


class ChannelTypeRegexp(Enum):
    """
    Regular expression to match available channels types in a parquet file
    """

    vel = "^vel[0-9]*.[0-9]*"
    std = "^std[0-9]*.[0-9]*$(?<!detrend)"
    std_dtr = "^std[0-9]*.[0-9]*_detrend$"
    temp = "^temp[0-9]*.[0-9]*"
    hum = "^hum[0-9]*.[0-9]*"
    press = "^press[0-9]*.[0-9]*"
    dir = "^dir[0-9]*.[0-9]*"
    sdir = "sdir"

    def __str__(self):

        return str(self.value)


class StatsManagerException(Exception):
    """
    Custom exception class
    """

    def __init__(self, code, message):

        self.status_code = code
        self.message = message

        super().__init__(self.message)
