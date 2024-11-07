import requests
import json
import datetime
import pandas as pd

# Hämta data från API
url = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/18.021515/lat/59.30996/data.json'
response = requests.get(url)
json_data = json.loads(response.text)

# Endast de första 24 timmarna av data
time_series_data = json_data['timeSeries'][:24]

# Nuvarande tid och 24-timmars intervall
now = datetime.datetime.now()
now_24 = now + datetime.timedelta(hours=24)
added_rows = 0

# Lista för att samla data
data = []

# Iterera över varje tidsdata
for time_param in time_series_data:
    temp, rain, wind = None, None, None  # Återställ värden varje iteration
    for time_data in time_param['parameters']:
        if time_data['unit'] == 'Cel':
            temp = time_data['values'][0]
        elif time_data['name'] == 'pcat':
            rain = time_data['values'][0]
        elif time_data['name'] == 'ws':
            wind = time_data['values'][0]

    # Gå vidare om alla nödvändiga värden finns
    if temp is not None and rain is not None and wind is not None:
        result = rain >= 1  # Kontrollera om det regnar
        now_hour_formatted = now.strftime('%H')
        now_formatted = now.strftime('%Y-%m-%d')
        
        # Lägg till data i listan
        data.append([now_formatted, now_hour_formatted, temp, result])
        added_rows += 1

        # Avsluta om 24 poster har samlats in
        if added_rows >= 24:
            break

    # Inkrementera timme för nästa tidsintervall
    now += datetime.timedelta(hours=1)
# Skapa DataFrame från insamlad data
# Skapa DataFrame från insamlad data
df = pd.DataFrame(data, columns=["Datum", "Timme", "Temperatur (°C)", "Regn (True/False)"])

# Visa tabellen utan index
print(df.to_string(index=False))


