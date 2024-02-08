[![Python application](https://github.com/javierjsa/stats-api/actions/workflows/python-app.yml/badge.svg)](https://github.com/javierjsa/stats-api/actions/workflows/python-app.yml)
[![Pylint](https://github.com/javierjsa/stats-api/actions/workflows/pylint.yml/badge.svg)](https://github.com/javierjsa/stats-api/actions/workflows/pylint.yml)
# <span style="color:green">Channel stats API
Fastapi application that works with parquet files containing meteorological data from different sensors:
- Upload a file, there is a sample in resources folder.
- Request available channels, providing a file identifier and optionally, a type of channel.
- Request statistics for certains channels within a date range.

## <span style="color:green">Endpoints


- ### /channels  
    Retrieve available channel identifiers per type.<br/><br/>
    - Allowed channel types are: vel, std, std_dtr, temp, hum, press, dir, sdir.<br/>
    - Requesting a channel type outside allowed values will raise an error.
    - Duplicated channel types are filtered before processing.<br/><br/>

    **Receives**: _ChannelRequest_ model with a file identifier and an optional list of channel_type values.<br/>
    **Returns**: _Channels_ model with dictionary of available channels sorted by channel type.
- ### /stats
    Retrieve stats (mean and standard deviation) for requested file identifier and channel identifiers.<br/><br/>

    - In case no channel is specified, stats for all channels are returned.
    - A date range may be provided, otherwise stats are computed for the whole time series.
    - Should only start_date be specified, end_date is set to now.
    - Providing any nonexistent channel identifier will raise an error<br/><br/>

    **Receives**: _StatsRequest_ model with a file identifier and optionally, a list of channels and  a date range.<br/>
    **Returns**:  Dictionary of _Stats_ models including dictionary of dictionaries with stats sorted by channel.
- ### /upload
    Upload a parquet file to an object storage backend. Files can only be uploaded once and are assigned an identifier based on the file hash.<br/><br/> 
    
    **Receives**: Parquet file.<br/>
    **Returns**: _FileId_ model containing _file_id_ and _stored_ values. If an identical file has been uploaded before, _stored_ is false, meaning file was not re-uploaded.
    

## <span style="color:green">Docker image

- ### Download image:</br>
      docker pull javierjsa/statsapi:latest

- ### Run docker compose:</br>
      docker-compose -f docker-compose.yaml up
 
- ### Access documentation:</br>
      http://0.0.0.0/docs


