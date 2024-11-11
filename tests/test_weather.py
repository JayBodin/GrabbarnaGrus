import sys
from flask import Flask, render_template
import requests
import json
import datetime
import pandas as pd
import unittest
from unittest.mock import patch
import numpy as np

app = Flask(__name__)

def fetch_weather_data():
    url = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/18.021515/lat/59.30996/data.json'
    response = requests.get(url)
    json_data = json.loads(response.text)

    time_series_data = json_data['timeSeries'][:24]
    now = datetime.datetime.now()
    data = []

    for time_param in time_series_data:
        temp, rain = None, None
        for time_data in time_param['parameters']:
            if 'unit' in time_data and time_data['unit'] == 'Cel':
                temp = time_data['values'][0]
            elif 'name' in time_data and time_data['name'] == 'pcat':
                rain = time_data['values'][0]

        if temp is not None and rain is not None:
            try:
                rain = float(rain)
            except ValueError:
                rain = 0.0

            result = rain >= 1
            now_hour_formatted = now.strftime('%H')
            now_formatted = now.strftime('%Y-%m-%d')
            data.append([now_formatted, now_hour_formatted, temp, result])
            now += datetime.timedelta(hours=1)

    df = pd.DataFrame(data, columns=["Datum", "Timme", "Temperatur (°C)", "Regn (True/False)"])
    return df

@app.route('/')
def index():
    weather_df = fetch_weather_data()
    weather_data = weather_df.to_dict(orient='records')
    return render_template('weather.html', weather_data=weather_data)





class TestSMHIAPIIntegration(unittest.TestCase):

    @patch('requests.get')
    def test_api_successful(self, mock_get):
        mock_response = {
            'timeSeries': [{
                'parameters': [
                    {'unit': 'Cel', 'values': [15]},
                    {'name': 'pcat', 'values': [0.5]}
                ]
            }]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = json.dumps(mock_response)
        weather_data = fetch_weather_data()
        self.assertIsInstance(weather_data, pd.DataFrame)
        self.assertGreater(len(weather_data), 0)

    @patch('requests.get')
    def test_api_500_error(self, mock_get):
        mock_get.return_value.status_code = 500
        mock_get.return_value.text = 'Internal Server Error'
        with self.assertRaises(Exception):
            fetch_weather_data()

    @patch('requests.get')
    def test_api_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout
        with self.assertRaises(requests.exceptions.Timeout):
            fetch_weather_data()

    @patch('requests.get')
    def test_api_invalid_json(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "invalid json"
        with self.assertRaises(ValueError):
            fetch_weather_data()

    @patch('requests.get')
    def test_api_invalid_structure(self, mock_get):
        mock_response = {
            'timeSeries': [{
                'parameters': [
                    {'unit': 'Cel', 'values': [15]},
                    {'name': 'pcat', 'values': ['invalid']}
                ]
            }]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = json.dumps(mock_response)
        weather_data = fetch_weather_data()
        self.assertEqual(weather_data.iloc[0]['Regn (True/False)'], False)


class TestWeatherDataProcessing(unittest.TestCase):

    def test_data_processing(self):
        mock_json_data = {
            'timeSeries': [{
                'parameters': [
                    {'unit': 'Cel', 'values': [15]},
                    {'name': 'pcat', 'values': [0.5]}
                ]
            }]
        }
        now = datetime.datetime.now()
        data = []
        for time_param in mock_json_data['timeSeries']:
            temp, rain = None, None
            for time_data in time_param['parameters']:
                if 'unit' in time_data and time_data['unit'] == 'Cel':
                    temp = time_data['values'][0]
                elif 'name' in time_data and time_data['name'] == 'pcat':
                    rain = time_data['values'][0]
            if temp is not None and rain is not None:
                try:
                    rain = float(rain)
                except ValueError:
                    rain = 0.0

                result = rain >= 1
                now_hour_formatted = now.strftime('%H')
                now_formatted = now.strftime('%Y-%m-%d')
                data.append([now_formatted, now_hour_formatted, temp, result])
                now += datetime.timedelta(hours=1)

        df = pd.DataFrame(data, columns=["Datum", "Timme", "Temperatur (°C)", "Regn (True/False)"])

        self.assertEqual(df.iloc[0]['Temperatur (°C)'], 15)
        self.assertEqual(df.iloc[0]['Regn (True/False)'], False)
        self.assertTrue(isinstance(df.iloc[0]['Temperatur (°C)'], (int, float, np.int64)))
        self.assertTrue(isinstance(df.iloc[0]['Regn (True/False)'], (bool, np.bool_)))

    def test_edge_case_missing_data(self):
        mock_json_data = {
            'timeSeries': [{
                'parameters': [
                    {'unit': 'Cel', 'values': [None]},
                    {'name': 'pcat', 'values': [0.5]}
                ]
            }]
        }
        now = datetime.datetime.now()
        data = []
        for time_param in mock_json_data['timeSeries']:
            temp, rain = None, None
            for time_data in time_param['parameters']:
                if 'unit' in time_data and time_data['unit'] == 'Cel':
                    temp = time_data['values'][0]
                elif 'name' in time_data and time_data['name'] == 'pcat':
                    rain = time_data['values'][0]
            if temp is not None and rain is not None:
                try:
                    rain = float(rain)
                except ValueError:
                    rain = 0.0

                result = rain >= 1
                now_hour_formatted = now.strftime('%H')
                now_formatted = now.strftime('%Y-%m-%d')
                data.append([now_formatted, now_hour_formatted, temp, result])
                now += datetime.timedelta(hours=1)

        df = pd.DataFrame(data, columns=["Datum", "Timme", "Temperatur (°C)", "Regn (True/False)"])
        self.assertEqual(len(df), 0)


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if result.wasSuccessful():
        print('tests successfull!')