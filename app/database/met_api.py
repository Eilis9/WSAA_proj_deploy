# Getting some met data from the met api
import json
from pprint import pprint
import pandas as pd
import requests

url = "https://prodapi.metweb.ie/monthly-data/Athenry"


def get_met(url, weather_var, year):
# Make the request to the API
  response = requests.get(url)

  weather_vars = ['total_rainfall', 'soil_temperature', 'mean_temperature', 'solar_radiation', 
                'evaporation', 'degree_days_below_fiften_point_five_degrees_celsius', 'potential_evapotranspiration']
 # vars_dict = {'rain':'total_rainfall', 'stemp':'soil_temperature', 'temp':'mean_temperature', 'srad':'solar_radiation', 
  #              'evap': 'evaporation', 'ddaysub5': 'degree_days_below_fiften_point_five_degrees_celsius', 'pote': 'potential_evapotranspiration'}
 
  # Filter reports for the given year


# Check if the request is successful
  if response.status_code == 200:
      data = response.json()
      # filter for the required data
      selected_data = data.get(weather_var, {}).get('report', {}).get(year, {})
      # Check if ['annual'] is in data
      if 'annual' in selected_data:
        del selected_data['annual']
  else:
      print(f"Failed to retrieve data. Status code: {response.status_code}")


 
  return selected_data

