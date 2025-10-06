import openmeteo_requests

from openmeteo_sdk.Variable import Variable
from openmeteo_sdk.Aggregation import Aggregation

import pandas as pd
import requests_cache
from retry_requests import retry
import numpy as np
import random
import streamlit as st

class OpenMeteoAPI:
    def __init__(self):
        self.loco_coord_dict = {
            "NYC": ('40.77898', '-73.96925'),
            "Miami": ('25.78805', '-80.31694'),
            "Chicago": ('41.73727', '-87.77734'),
            "Denver": ('39.84657', '-104.65623'),
            "Austin": ('30.18311', '-97.67989'),
            "Los Angeles": ('33.93816', '-118.3866'),
            "Philadelphia": ('39.87326', '-75.22681')
        }

        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        self.openmeteo = openmeteo_requests.Client(session = retry_session)

        self.models = ["gfs_seamless","gfs025","gfs05","ecmwf_ifs025","ecmwf_aifs025","gem_global"]

    @st.cache_data
    def pull_forecast(_self, forecast, location, models):
        coordinates = _self.loco_coord_dict[location]

        url = "https://ensemble-api.open-meteo.com/v1/ensemble"

        params = {
            "latitude": coordinates[0],
            "longitude": coordinates[1],
            "daily": "temperature_2m_max",
            "timezone": "auto",
            "models": models,
            "forecast_days": 3,
        }

        responses = _self.openmeteo.weather_api(url, params=params)
        min_len = 1e9

        for response in responses:
            daily = response.Daily()
            min_len = min(len(list(map(lambda i: daily.Variables(i), range(0, daily.VariablesLength())))),min_len) 

        daily_variables = []
        for response in responses:
            daily = response.Daily()
            daily_variables += random.sample(list(map(lambda i: daily.Variables(i), range(0, daily.VariablesLength()))),min_len)

        daily_max_temperature_2m = filter(lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2, daily_variables)

        data = np.zeros((len(daily_variables),3))
        
        convert = np.vectorize(lambda celsius: (celsius * 9/5) + 32)

        for i, variable in enumerate(daily_max_temperature_2m):
            data[i] = convert(variable.ValuesAsNumpy())

          
        if forecast == "Today":
            return data[:,0]
        else:
            return data[:,1]
        
    @st.cache_data
    def pull_backtest(_self, forecast, location, models):
        if forecast != "Tomorrow":
            raise Exception("Only Backtest on tomorrow trades")
        
        # First pull the max history
        coordinates = _self.loco_coord_dict[location]

        url = "https://ensemble-api.open-meteo.com/v1/ensemble"

        params = {
            "latitude": coordinates[0],
            "longitude": coordinates[1],
            "daily": "temperature_2m_max",
            "timezone": "auto",
            "models": models,
            "forecast_days": 7,
            "past_days": 92,
        }

        responses = _self.openmeteo.weather_api(url, params=params)

        min_len = 1e9
        for response in responses:
            daily = response.Daily()
            min_len = min(len(list(map(lambda i: daily.Variables(i), range(0, daily.VariablesLength())))),min_len) 

        # Process daily data. The order of variables needs to be the same as requested.
        daily_variables = []
        for response in responses:
            daily = response.Daily()
            daily_variables += random.sample(list(map(lambda i: daily.Variables(i), range(0, daily.VariablesLength()))),min_len)

        daily_temperature_2m_max = filter(lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2, daily_variables)	

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
	        inclusive = "left"
        )}
        
        # Process all daily members
        for variable in daily_temperature_2m_max:
            member = variable.EnsembleMember()
            daily_data[f"temperature_2m_max_member{member}"] = variable.ValuesAsNumpy()

        daily_dataframe_forecasts = pd.DataFrame(data = daily_data)
        daily_dataframe_forecasts = daily_dataframe_forecasts.dropna(how='any')
        
        min_date = min(daily_dataframe_forecasts["date"])
        max_date = max(daily_dataframe_forecasts["date"])

        params = {
            "latitude": coordinates[0],
            "longitude": coordinates[1],
            "start_date": str(min_date).split(' ')[0],
            "end_date": str(max_date).split(' ')[0],
            "daily": "temperature_2m_max",
            "timezone": "auto",
        }
        responses = _self.openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models

        response = responses[0]

        # Process daily data. The order of variables needs to be the same as requested.

        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()

        daily_dataframe_forecasts["temperature_2m_max"] = daily_temperature_2m_max        

        return daily_dataframe_forecasts

    def get_models(self):
        return self.models
