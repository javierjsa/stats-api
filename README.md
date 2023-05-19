# Channel stats API
Fastapi application consisting of two endpoints:

- **/channels?channel_type** Returns a list of available channels of requested channel type. If no channel type is specified, all availables channels are returned
- **/stats?channel_name?start_date?end_date** Computes stats for each specified channels whithin start_date - end_date range.<br/>If no channel is specified, stats for all channels are computed.
  if no data range is specified, stats are computed for the whole time series.
