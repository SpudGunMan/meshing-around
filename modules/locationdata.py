# helper functions to use location data
# K7MHI Kelly Keeton 2024

import json # pip install json
from geopy.geocoders import Nominatim # pip install geopy
import maidenhead as mh # pip install maidenhead
import requests # pip install requests
import bs4 as bs # pip install beautifulsoup4
import xml.dom.minidom 

URL_TIMEOUT = 10 # wait time for URL requests
DAYS_OF_WEATHER = 4 # weather forecast days, the first two rows are today and tonight
# error messages
ALERT_COUNT = 2 # number of weather alerts to display
NO_DATA_NOGPS = "no location data: does your device have GPS?"
ERROR_FETCHING_DATA = "error fetching data"

trap_list_location = ("whereami", "tide", "moon", "wx", "wxc", "wxa", "wxalert")

def where_am_i(lat=0, lon=0):
    whereIam = ""
    if float(lat) == 0 and float(lon) == 0:
        return NO_DATA_NOGPS
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="mesh-bot")

    location = geolocator.reverse(lat + ", " + lon)
    address = location.raw['address']
    address_components = ['house_number', 'road', 'city', 'state', 'postcode', 'county', 'country']
    whereIam += ' '.join([address.get(component, '') for component in address_components if component in address])
    grid = mh.to_maiden(float(lat), float(lon))
    whereIam += " Grid: " + grid

    return whereIam

def get_tide(lat=0, lon=0):
    station_id = ""
    if float(lat) == 0 and float(lon) == 0:
        return NO_DATA_NOGPS
    station_lookup_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/tidepredstations.json?lat=" + str(lat) + "&lon=" + str(lon) + "&radius=50"
    try:
        station_data = requests.get(station_lookup_url, timeout=URL_TIMEOUT)
        if station_data.ok:
            station_json = station_data.json()
        else:
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException, json.JSONDecodeError):
        return ERROR_FETCHING_DATA

    if station_id is None:
            return "no tide station found"
    
    station_id = station_json['stationList'][0]['stationId']

    station_url = "https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=" + station_id

    try:
        station_data = requests.get(station_url, timeout=URL_TIMEOUT)
        if not station_data.ok:
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        return ERROR_FETCHING_DATA
    
    # extract table class="table table-condensed"
    soup = bs.BeautifulSoup(station_data.text, 'html.parser')
    table = soup.find('table', class_='table table-condensed')

    # extract rows
    rows = table.find_all('tr')
    # extract data from rows
    tide_data = []
    for row in rows:
        row_text = ""
        cols = row.find_all('td')
        for col in cols:
            row_text += col.text + " "
        tide_data.append(row_text)
    # format tide data into a string
    tide_string = ""
    for data in tide_data:
        tide_string += data + "\n"
    # trim off last newline
    tide_string = tide_string[:-1]
    return tide_string
    
def get_weather(lat=0, lon=0, unit=0):
    # get weather report from NOAA for forecast detailed
    weather = ""
    if float(lat) == 0 and float(lon) == 0:
        return NO_DATA_NOGPS
    
    # get weather data from NOAA units for metric
    weather_url = "https://forecast.weather.gov/MapClick.php?FcstType=text&lat=" + str(lat) + "&lon=" + str(lon)
    if unit == 1:
        weather_url += "&unit=1"
    
    try:
        weather_data = requests.get(weather_url, timeout=URL_TIMEOUT)
        if not weather_data.ok:
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        return ERROR_FETCHING_DATA
    
    soup = bs.BeautifulSoup(weather_data.text, 'html.parser')
    table = soup.find('div', id="detailed-forecast-body")

    if table is None:
        return "no weather data found on NOAA for your location"
    else:
        # get rows
        rows = table.find_all('div', class_="row")

    # extract data from rows
    for row in rows:
        # shrink the text
        line = abbreviate_weather(row.text)
        # only grab a few days of weather
        if len(weather.split("\n")) < DAYS_OF_WEATHER:
            weather += line + "\n"
    # trim off last newline
    weather = weather[:-1]

    # get any alerts and return the count
    alert_num = getWeatherAlerts(lat, lon)[1]
    if alert_num > 0:
        # add the alert count warning to the weather
        weather = str(alert_num) + " local alerts!\n" + weather

    return weather

def abbreviate_weather(row):
    # replace long strings with shorter ones for display used in get_weather, get_wx_alerts_list, get_wx_alert_details
    replacements = {
        "Monday": "Mon ",
        "Tuesday": "Tue ",
        "Wednesday": "Wed ",
        "Thursday": "Thu ",
        "Friday": "Fri ",
        "Saturday": "Sat ",
        "Today": "Today ",
        "Night": "Night ",
        "Tonight": "Tonight ",
        "Tomorrow": "Tomorrow ",
        "Day": "Day ",
        "This Afternoon": "Afternoon ",
        "Overnight": "Overnight ",
        "northwest": "NW",
        "northeast": "NE",
        "southwest": "SW",
        "southeast": "SE",
        "north": "N",
        "south": "S",
        "east": "E",
        "west": "W",
        "Northwest": "NW",
        "Northeast": "NE",
        "Southwest": "SW",
        "Southeast": "SE",
        "North": "N",
        "South": "S",
        "East": "E",
        "West": "W",
        "precipitation": "precip",
        "showers": "shwrs",
        "thunderstorms": "t-storms"
    }

    line = row
    for key, value in replacements.items():
        line = line.replace(key, value)
                    
    return line

def getWeatherAlerts(lat=0, lon=0):
    # get weather alerts from NOAA limited to ALERT_COUNT with the total number of alerts found
    alerts = ""
    if float(lat) == 0 and float(lon) == 0:
        return NO_DATA_NOGPS

    alert_url = "https://api.weather.gov/alerts/active.atom?point=" + str(lat) + "," + str(lon)
    #alert_url = "https://api.weather.gov/alerts/active.atom?area=WA"
    
    try:
        alert_data = requests.get(alert_url, timeout=URL_TIMEOUT)
        if not alert_data.ok:
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        return ERROR_FETCHING_DATA
    
    alerts = ""
    alertxml = xml.dom.minidom.parseString(alert_data.text)

    for i in alertxml.getElementsByTagName("entry"):
        alerts += (
            i.getElementsByTagName("title")[0].childNodes[0].nodeValue + "\n"
        )

    if alerts == "":
        return "No weather alerts found"

    # trim off last newline
    if alerts[-1] == "\n":
        alerts = alerts[:-1]
        
    # get the number of alerts
    alert_num = 0
    alert_num = len(alerts.split("\n"))

    alerts = abbreviate_weather(alerts)

    # return the first ALERT_COUNT alerts
    return "\n".join(alerts.split("\n")[:ALERT_COUNT]), alert_num

def getActiveWeatherAlertsDetail(lat=0, lon=0):
    # get the latest details of weather alerts from NOAA
    alerts = ""
    if float(lat) == 0 and float(lon) == 0:
        return NO_DATA_NOGPS

    alert_url = "https://api.weather.gov/alerts/active.atom?point=" + str(lat) + "," + str(lon)
    #alert_url = "https://api.weather.gov/alerts/active.atom?area=WA"
    
    try:
        alert_data = requests.get(alert_url, timeout=URL_TIMEOUT)
        if not alert_data.ok:
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        return ERROR_FETCHING_DATA
    
    alerts = ""
    alertxml = xml.dom.minidom.parseString(alert_data.text)

    for i in alertxml.getElementsByTagName("entry"):
        summary = i.getElementsByTagName("summary")[0].childNodes[0].nodeValue
        summary = summary.replace("\n\n", " ")
        summary = summary.replace("\n", " ")
        summary = summary.replace("*", "\n")

        alerts += (
            i.getElementsByTagName("title")[0].childNodes[0].nodeValue +
            summary +
            "\n***\n"
        )

    alerts = abbreviate_weather(alerts)

    # trim the alerts to the first ALERT_COUNT
    alerts = alerts.split("\n***\n")[:ALERT_COUNT]

    if alerts == "":
        return "No weather alerts found"

    # trim off last newline
    if alerts[-1] == "\n":
        alerts = alerts[:-1]

    # return the first ALERT_COUNT alerts
    return alerts