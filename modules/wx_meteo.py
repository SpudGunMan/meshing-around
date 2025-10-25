#import openmeteo_requests # pip install openmeteo-requests
#from retry_requests import retry # pip install retry_requests

import requests
import json
from modules.log import logger
from modules.settings import ERROR_FETCHING_DATA

def get_weather_data(api_url, params):
    response = requests.get(api_url, params=params)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()

def get_wx_meteo(lat=0, lon=0, unit=0):
	# set forcast days 1 or 3
	forecastDays = 3

	# Make sure all required weather variables are listed here
	# The order of variables in hourly or daily is important to assign them correctly below
	url = "https://api.open-meteo.com/v1/forecast"
	params = {
		"latitude": {lat},
		"longitude": {lon},
		"daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_hours", "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"],
		"timezone": "auto",
		"forecast_days": {forecastDays}
	}

	# Unit 0 is imperial, 1 is metric
	if unit == 0:
		params["temperature_unit"] = "fahrenheit"
		params["wind_speed_unit"] = "mph"
		params["precipitation_unit"] = "inch"
		params["distance_unit"] = "mile"
		params["pressure_unit"] = "inHg"

	try:
		# Fetch the weather data
		weather_data = get_weather_data(url, params)
	except Exception as e:
		logger.error(f"Error fetching meteo weather data: {e}")
		return ERROR_FETCHING_DATA

	# Check if we got a response
	try:
		# Process location
		logger.debug(f"System: Pulled from Open-Meteo in {weather_data['timezone']} {weather_data['timezone_abbreviation']}")
		
		# Ensure response is defined
		response = weather_data
		
		# Process daily data. The order of variables needs to be the same as requested.
		daily = response['daily']
		daily_weather_code = daily['weather_code']
		daily_temperature_2m_max = daily['temperature_2m_max']
		daily_temperature_2m_min = daily['temperature_2m_min']
		daily_precipitation_hours = daily['precipitation_hours']
		daily_precipitation_probability_max = daily['precipitation_probability_max']
		daily_wind_speed_10m_max = daily['wind_speed_10m_max']
		daily_wind_gusts_10m_max = daily['wind_gusts_10m_max']
		daily_wind_direction_10m_dominant = daily['wind_direction_10m_dominant']
	except Exception as e:
		logger.error(f"Error processing meteo weather data: {e}")
		return ERROR_FETCHING_DATA

	# convert wind value to cardinal directions
	for value in daily_wind_direction_10m_dominant:
		if value < 22.5:
			wind_direction = "N"
		elif value < 67.5:
			wind_direction = "NE"
		elif value < 112.5:
			wind_direction = "E"
		elif value < 157.5:
			wind_direction = "SE"
		elif value < 202.5:
			wind_direction = "S"
		elif value < 247.5:
			wind_direction = "SW"
		elif value < 292.5:
			wind_direction = "W"
		elif value < 337.5:
			wind_direction = "NW"
		else:
			wind_direction = "N"

	# create a weather report
	weather_report = ""
	for i in range(forecastDays):
		if str(i + 1) == "1":
			weather_report += "Today, "
		elif str(i + 1) == "2":
			weather_report += "Tomorrow, "
		else:
			weather_report += "Futurecast: "
		
		# report weather from WMO Weather interpretation codes (WW)
		code_string = ""
		if daily_weather_code[i] == 0:
			code_string = "Clear sky"
		elif daily_weather_code[i] == 1:
			code_string = "Mostly Cloudy"
		elif daily_weather_code[i] == 2:
			code_string = "Partly Cloudy"
		elif daily_weather_code[i] == 3:
			code_string = "Overcast"
		elif daily_weather_code[i] == 5:
			code_string = "Haze"
		elif daily_weather_code[i] == 10:
			code_string = "Mist"
		elif daily_weather_code[i] == 45:
			code_string = "Fog"
		elif daily_weather_code[i] == 48:
			code_string = "Freezing Fog"
		elif daily_weather_code[i] == 51:
			code_string = "Drizzle: Light"
		elif daily_weather_code[i] == 53:
			code_string = "Drizzle: Moderate"
		elif daily_weather_code[i] == 55:
			code_string = "Drizzle: Heavy"
		elif daily_weather_code[i] == 56:
			code_string = "Freezing Drizzle: Light"
		elif daily_weather_code[i] == 57:
			code_string = "Freezing Drizzle: Moderate"
		elif daily_weather_code[i] == 61:
			code_string = "Rain: Slight"
		elif daily_weather_code[i] == 63:
			code_string = "Rain: Moderate"
		elif daily_weather_code[i] == 65:
			code_string = "Rain: Heavy"
		elif daily_weather_code[i] == 66:
			code_string = "Freezing Rain: Light"
		elif daily_weather_code[i] == 67:
			code_string = "Freezing Rain: Dense"
		elif daily_weather_code[i] == 71:
			code_string = "Snow: Light"
		elif daily_weather_code[i] == 73:
			code_string = "Snow: Moderate"
		elif daily_weather_code[i] == 75:
			code_string = "Snow: Heavy"
		elif daily_weather_code[i] == 77:
			code_string = "Snow Grains"
		elif daily_weather_code[i] == 78:
			code_string = "Ice Crystals"
		elif daily_weather_code[i] == 79:
			code_string = "Ice Pellets"
		elif daily_weather_code[i] == 80:
			code_string = "Rain showers: Slight"
		elif daily_weather_code[i] == 81:
			code_string = "Rain showers: Moderate"
		elif daily_weather_code[i] == 82:
			code_string = "Rain showers: Heavy"
		elif daily_weather_code[i] == 85:
			code_string = "Snow showers"
		elif daily_weather_code[i] == 86:
			code_string = "Snow showers: Heavy"
		elif daily_weather_code[i] == 95:
			code_string = "Thunderstorm"
		elif daily_weather_code[i] == 96:
			code_string = "Hailstorm"
		elif daily_weather_code[i] == 97:
			code_string = "Thunderstorm Heavy"
		elif daily_weather_code[i] == 99:
			code_string = "Hailstorm Heavy"

		weather_report += "Cond: " + code_string + ". "

		# report temperature
		if unit == 0:
			weather_report += "High: " + str(int(round(daily_temperature_2m_max[i]))) + "F, with a low of " + str(int(round(daily_temperature_2m_min[i]))) + "F. "
		else:
			weather_report += "High: " + str(int(round(daily_temperature_2m_max[i]))) + "C, with a low of " + str(int(round(daily_temperature_2m_min[i]))) + "C. "

		# check for precipitation
		if daily_precipitation_hours[i] > 0:
			if unit == 0:
				weather_report += "Precip: " + str(round(daily_precipitation_probability_max[i],2)) + "in, in " + str(round(daily_precipitation_hours[i],2)) + " hours. "
			else:
				weather_report += "Precip: " + str(round(daily_precipitation_probability_max[i],2)) + "mm, in " + str(round(daily_precipitation_hours[i],2)) + " hours. "
		else:
			weather_report += "No Precip. "

		# check for wind
		if daily_wind_speed_10m_max[i] > 0:
			if unit == 0:
				weather_report += "Wind: " + str(int(round(daily_wind_speed_10m_max[i]))) + "mph, gusts up to " + str(int(round(daily_wind_gusts_10m_max[i]))) + "mph from:" + wind_direction + "."
			else:
				weather_report += "Wind: " + str(int(round(daily_wind_speed_10m_max[i]))) + "kph, gusts up to " + str(int(round(daily_wind_gusts_10m_max[i]))) + "kph from:" + wind_direction + "."
		else:
			weather_report += "No Wind\n"

		# add a new line for the next day
		if i < forecastDays - 1:
			weather_report += "\n"

	return weather_report

def get_flood_openmeteo(lat=0, lon=0):
	# set forcast days 1 or 3
	forecastDays = 3

	# Flood data
	url = "https://flood-api.open-meteo.com/v1/flood"
	params = {
		"latitude": {lat},
		"longitude": {lon},
		"timezone": "auto",
		"daily": "river_discharge",
		"forecast_days": forecastDays
	}

	try:
		# Fetch the flood data
		flood_data = get_weather_data(url, params)
	except Exception as e:
		logger.error(f"Error fetching meteo flood data: {e}")
		return ERROR_FETCHING_DATA
	
	# Check if we got a response
	try:
		# Process location
		logger.debug(f"System: Pulled River FLow Data from Open-Meteo {flood_data['timezone_abbreviation']}")
		
		# Ensure response is defined
		response = flood_data
		
		# Process daily data. The order of variables needs to be the same as requested.
		daily = response['daily']
		daily_river_discharge = daily['river_discharge']
		# check if none

	except Exception as e:
		logger.error(f"Error processing meteo flood data: {e}")
		return ERROR_FETCHING_DATA
	
	# create a flood report
	flood_report = ""
	flood_report += "River Discharge: " + str(daily_river_discharge) + "m3/s"

	return flood_report
