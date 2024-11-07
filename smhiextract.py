import requests
import json
import datetime
import time
import pandas as p

url = (f'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/18.021515/lat/59.30996/data.json')
response = requests.get(url)
json_data = json.loads(response.text)

time_series_data = json_data['timeSeries'][:24]

now = datetime.datetime.now()
now_formaterad = now.strftime('%Y-%m-%d')
nu = datetime.datetime.now()
now_24 = now.strftime('%Y-%m-%d')
now_24 = now + datetime.timedelta(hours=24)
added_rows = 0

for time_param in time_series_data:
    for time_data in time_param['parameters']:
        if time_data['unit'] == 'Cel':
            temp = time_data['values'][0]
        if time_data['name'] == 'pcat':
            rain = time_data['values'][0]
        if time_data['name'] == 'ws':
            wind = time_data['values'][0]
            while (now < now_24):
                    nu = now + datetime.timedelta(hours=1)
                    now_formaterad = now.strftime('%Y-%m-%d')
                    now_hour_formaterad = nu.strftime('%H')
                    now = now + datetime.timedelta(hours=1)
                    if rain >= 1:
                        result = True
                    else:
                        result = False

                    all_data = [now_formaterad, now_hour_formaterad, temp, result]
                    for row in all_data:
                        print(all_data)
                        added_rows += 1
                    if  added_rows >= 24:
                        break
