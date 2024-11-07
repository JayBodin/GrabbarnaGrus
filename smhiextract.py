import requests
import json
import datetime

# Fetch data from API
url = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/18.021515/lat/59.30996/data.json'
response = requests.get(url)
json_data = json.loads(response.text)

# Only the first 24 hours of data
time_series_data = json_data['timeSeries'][:24]

# Set current time and 24-hour range
now = datetime.datetime.now()
now_24 = now + datetime.timedelta(hours=24)
added_rows = 0

# Iterate over each time point
for time_param in time_series_data:
    temp, rain, wind = None, None, None  # Reset values each loop
    for time_data in time_param['parameters']:
        if time_data['unit'] == 'Cel':
            temp = time_data['values'][0]
        elif time_data['name'] == 'pcat':
            rain = time_data['values'][0]
        elif time_data['name'] == 'ws':
            wind = time_data['values'][0]

    # Proceed if all required values are present
    if temp is not None and rain is not None and wind is not None:
        result = rain >= 1
        now_hour_formatted = now.strftime('%H')
        now_formatted = now.strftime('%Y-%m-%d')
        
        # Collect data for this time point
        all_data = [now_formatted, now_hour_formatted, temp, result]
        print(all_data)  # Print without nested loop
        added_rows += 1

        # Stop if 24 entries are collected
        if added_rows >= 24:
            break

    # Increment hour for next time point
    now += datetime.timedelta(hours=1)
