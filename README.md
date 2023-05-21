# <span style="color:green">Channel stats API
Fastapi application consisting of two endpoints:

## <span style="color:green">Endpoints


- ### /channels  
    Retrieve available channel identifiers per type.<br/><br/>
    - Allowed channel types are: vel, std, std_dtr, temp, hum, press, dir, sdir.<br/>
    - Requesting a channels type outside allowed values will raise an error.
    - Duplicated channel types are filtered before processing.<br/><br/>

    **Receives**: _ChannelRequest_ model with optional list of channel_type values.<br/>
    **Returns**: _Channels_ model with dictionary of available channels sorted by channel type.
- ### /stats
    Retrieve stats (mean and standard deviation) for requested channel identifiers.<br/><br/>

    - In case no channel is specified, stats for all channels are returned.
    - A date range may be provided, otherwise stats are computed for the whole time series.
    - Should only start_date is specified, end_date is set to now.
    - Providing any nonexistent channel identifiers will raise an error<br/><br/>

    **Receives**: _StatsRequest_ model including an optional list of channels and an optional date range.<br/>
    **Returns**:  Dictionary of _Stats_ models including dictionary of dictionaries with stats sorted by channel.

## <span style="color:green">Docker image

- ### Download image:</br>
      docker pull javierjsa/statsapi:latest</br>

- ### Run image:</br>
      docker run -t --rm -p 8000:8000 statsapi:latest
 
- ### Access documentation:</br>
      http://0.0.0.0:8000/docs


