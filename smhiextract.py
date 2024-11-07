import requests
import json
import datetime
import pandas as pd
import unittest

# Funktion för att hämta data från API och bearbeta det
def fetch_weather_data():
    url = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/18.021515/lat/59.30996/data.json'
    response = requests.get(url)
    json_data = json.loads(response.text)

    # Endast de första 24 timmarna av data
    time_series_data = json_data['timeSeries'][:24]
    now = datetime.datetime.now()
    now_24 = now + datetime.timedelta(hours=24)
    added_rows = 0
    data = []

    for time_param in time_series_data:
        temp, rain, wind = None, None, None
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
            data.append([now_formatted, now_hour_formatted, temp, result])
            added_rows += 1
            if added_rows >= 24:
                break
        now += datetime.timedelta(hours=1)

    # Skapa en DataFrame från insamlad data
    df = pd.DataFrame(data, columns=["Datum", "Timme", "Temperatur (°C)", "Regn (True/False)"])
    return df

# Visa tabellen
df = fetch_weather_data()
print(df.to_string(index=False))


# Integrationstester
class TestSMHIAPIIntegration(unittest.TestCase):
    
    def setUp(self):
        self.url = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/18.021515/lat/59.30996/data.json'

    def test_api_status_code(self):
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200, "API-anropet misslyckades. Statuskod är inte 200.")

    def test_api_response_format(self):
        response = requests.get(self.url)
        data = response.json()
        self.assertIn('timeSeries', data, "Nyckeln 'timeSeries' saknas i API-svaret.")
        self.assertIsInstance(data['timeSeries'], list, "'timeSeries' bör vara en lista.")
        if data['timeSeries']:
            first_entry = data['timeSeries'][0]
            self.assertIn('validTime', first_entry, "Nyckeln 'validTime' saknas i tidsseriedata.")
            self.assertIn('parameters', first_entry, "Nyckeln 'parameters' saknas i tidsseriedata.")
            self.assertIsInstance(first_entry['parameters'], list, "'parameters' bör vara en lista.")

    def test_data_values(self):
        response = requests.get(self.url)
        data = response.json()
        for time_entry in data['timeSeries']:
            for param in time_entry['parameters']:
                if param['unit'] == 'Cel':
                    temperature = param['values'][0]
                    self.assertTrue(-40 <= temperature <= 50, f"Temperaturen {temperature} är utanför det förväntade intervallet.")

# Kör testerna
if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2, exit=False)
