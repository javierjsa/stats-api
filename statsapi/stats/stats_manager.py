import os
from hashlib import md5
from io import BytesIO
from typing import Union, List, Dict, Any, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
import boto3
from statsapi.api.models import ChannelType
from statsapi.stats.utils import ChannelTypeRegexp, StatsManagerException


class StatsManager:
    """
    StatsManager contains the logic requires to store, load and process parquet files
    """

    def __init__(self):

        self.session = boto3.Session(aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                                     aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                                     aws_session_token=None)

    def get_channels(self, file_id: str, channel_type: List[ChannelType]) -> Dict[ChannelType, Any]:
        """
        Retrieve channels belonging to a certain channel type

        :param file_id: File identifier
        :type file_id: str
        :param channel_type: _description_
        :type channel_type: List[ChannelType]
        :return: Channels sorted by type
        :rtype: Dict[ChannelType, Any]
        """

        data = self._load_data(file_id)
        sorted_channels = self._sort_channels(data)

        if not channel_type:
            return sorted_channels

        return {ch.name: sorted_channels.get(ch.name, []) for ch in channel_type}

    def get_stats(self, file_id: str,
                  channel_ids: Union[List[str], None] = None,
                  start_date: str = None, end_date: str = None) -> Dict[str, float]:
        """
        Compute mean and standard deviation for a list of channel ids within date range.
        - If no channel identifiers are provided, all channels are used.
        - If no date range provided, full time series is used.
        - If start date provided, but no end date, end date is now.

        :param file_id: File identifier
        :type file_id: str
        :param channel_ids: List of channel identifiers, defaults to None
        :type channel_ids: Union[List[str], None], optional
        :param start_date: Start date in string format YYYY-m-d, defaults to None
        :type start_date: str, optional
        :param end_date: end date int string format YYYY-m-d, defaults to None
        :type end_date: str, optional
        :return: mean and standard deviation for requested channels.
        :rtype: Dict[str, float]
        """

        data = self._load_data(file_id)
        channel_ids = self._validate_column_names(data, channel_ids)

        data = self._select_date_range(data, start_date, end_date)
        data = data[channel_ids]

        mean = data.mean(skipna=True, numeric_only=True)
        std = data.std(skipna=True, numeric_only=True)

        stats = pd.concat([mean, std], axis=1)
        stats.rename(columns={0: "mean", 1: "std"}, inplace=True)
        stats = stats.replace(np.nan, None)
        stats = stats.to_dict('index')
        return stats

    def store_data(self, data: BytesIO) -> Tuple[str, bool]:
        """
        Save data to storage backend if it does not exist alreadt

        :param data: parquet data to be stored
        :type data: BytesIO
        :return: file hash as a file identifier and whether file was saved or not
        :rtype: str, bool
        """

        md5sum = md5(data.getbuffer())
        file_id = md5sum.hexdigest()
        client = self.session.client("s3", endpoint_url=os.environ.get("ENDPOINT"))
        data.seek(0)
        try:
            client.head_object(Bucket=os.environ.get("BUCKET"), Key=f"{file_id}.parquet")
            return file_id, False
        except Exception:
            try:
                client.put_object(Body=data, Bucket=os.environ.get("BUCKET"),
                                  Key=f"{file_id}.parquet", ContentType='application/x-parquet')
            except Exception as e:
                raise StatsManagerException(e)

        return file_id, True

    def _load_data(self, file_id: str) -> pd.DataFrame:
        """
        Load available data from storae backend and sort channels per type. Store in class variable

        :param file_id: file identifier
        :type file_id: str
        :return: requested data as a dataframe
        :rtype: pd.Daraframe
        """

        buffer = BytesIO()
        resource = self.session.resource("s3", endpoint_url=os.environ.get("ENDPOINT"))
        s3data = resource.Object(os.environ.get("BUCKET"), f"{file_id}.parquet")
        s3data.download_fileobj(buffer)
        dataframe = pd.read_parquet(buffer, engine='pyarrow')
        return dataframe

    def _sort_channels(self, data: pd.DataFrame) -> Dict[str, List[Any]]:
        """
        Sort available channels per channel type

        :param data: Dataframe to extract channels from
        :type data: pd.DataFrame
        :return: channels sorted by ChannelType
        :rtype: Dict[str, List[Any]]
        """

        sorted_channels = {}
        for ch in ChannelTypeRegexp:
            filtered_data = data.filter(regex=f"{ch.value}")
            sorted_channels[ch.name] = list(filtered_data.columns)
        return sorted_channels

    @staticmethod
    def _validate_dates(start_date: Union[str, datetime] = None,
                       end_date: Union[str, datetime] = None) -> Union[Tuple[datetime, datetime], Tuple[None, None]]:
        """
        Convert date strings to datetime objects. Dates are validated in case date strings are received.
        - If no date range provided, None is returned
        - If start date provided, but no end date, end date is now.
        - If validation fails, such as start_date greater than end_date, custom exception is raised

        :param start_date: Start date in string format YYYY-m-d, defaults to None
        :type start_date: Union[str, datetime], optional
        :param end_date: End date in string format YYYY-m-d, defaults to None
        :type end_date: Union[str, datetime], optional
        :raises StatsManagerException: Provided end data with no start date
        :raises StatsManagerException: date strings do not follow specified format
        :raises StatsManagerException: start date is greater than end date
        :return: parsed start and end dates
        :rtype: Union[Tuple[datetime, datetime], Tuple[None, None]]
        """

        if isinstance(start_date, datetime) and isinstance(end_date, datetime):
            return start_date, end_date

        if start_date is None and end_date is None:
            return None, None

        if start_date is None and end_date is not None:
            raise StatsManagerException(400, 'Cannot provide end_date without start_date')

        try:
            start_date = datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        except ValueError as error:
            raise StatsManagerException(400, str(error))

        if end_date is None:
            end_date = datetime.now()
        else:
            try:
                end_date = datetime.strptime(f"{end_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
            except ValueError as error:
                raise StatsManagerException(400, str(error))

        if start_date > end_date:
            raise StatsManagerException(400, f"Start_date {start_date} greater than end_date {end_date}")

        return start_date, end_date

    def _compute_mean(self, data: pd.DataFrame, channel_id: str) -> pd.Series:
        """
        Compute mean of channel identifier

        :param data: parquet data to be processed
        :type data: pd.DataFrame
        :param channel_id: channel identifier
        :type channel_id: str
        :return: computed mean
        :rtype: pd.Series
        """

        mean = data[channel_id].mean()
        return mean

    def _compute_std(self, data: pd.DataFrame, channel_id: str) -> pd.Series:
        """
        Compute standard deviation of channel identifier

        :param data: parquet data to be processed
        :type data: pd.DataFrame
        :param channel_id: channel identifier
        :type channel_id: str
        :return: computed standar deviation
        :rtype: pd.Series
        """

        std = data[channel_id].std()
        return std

    def _select_date_range(self, data: pd.DataFrame,
                          start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """
        Select date range from available data

        :param data: source parquet to extract data from
        :type data: pd.DataFrame
        :param start_date: start date, defaults to None
        :type start_date: datetime, optional
        :param end_date: end date, defaults to None
        :type end_date: datetime, optional
        :return: selected data
        :rtype: pd.DataFrame
        """

        start_date, end_date = self._validate_dates(start_date, end_date)

        if start_date is not None and end_date is not None:
            return data[(data.index >= start_date) & (data.index <= end_date)]

        return data

    def _validate_column_names(self, data: pd.DataFrame, channel_ids: List[str] = None) -> List[str]:
        """
        Check if list of provided channel identifiers is available. If any channel identifier is not available,
        an exception is raised.

        :param data: parque data to extract channels from
        :type data: pd.DataFrame
        :param channel_ids: list of channel identifiers, defaults to None
        :type channel_ids: list of available channels per type, optional
        :raises StatsManagerException: If any of requested channels is not available
        :rtype: List[str]
        """

        available_cols = list(data.columns)

        if not channel_ids:
            return available_cols

        filtered_channels_ids = []

        for ch in channel_ids:
            if ch in available_cols:
                filtered_channels_ids.append(ch)
            else:
                raise StatsManagerException(404, f"Channel_id {ch} is not available")

        return filtered_channels_ids
