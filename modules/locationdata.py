# helper functions to use location data like NOAA weather
# K7MHI Kelly Keeton 2024

import json # pip install json
from geopy.geocoders import Nominatim # pip install geopy
import maidenhead as mh # pip install maidenhead
import requests # pip install requests
import bs4 as bs # pip install beautifulsoup4
import xml.dom.minidom 
from modules.log import *

trap_list_location = ("whereami", "tide", "moon", "wx", "wxc", "wxa", "wxalert", "rlist", "ealert")

def where_am_i(lat=0, lon=0, short=False, zip=False):
    whereIam = ""
    grid = mh.to_maiden(float(lat), float(lon))
    
    if int(float(lat)) == 0 and int(float(lon)) == 0:
        logger.error("Location: No GPS data, try sending location")
        return NO_DATA_NOGPS
    
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="mesh-bot")
    
    try:
        # Nomatim API call to get address
        if short:
            location = geolocator.reverse(lat + ", " + lon)
            address = location.raw['address']
            address_components = ['city', 'state', 'county', 'country']
            whereIam = f"City: {address.get('city', '')}. State: {address.get('state', '')}. County: {address.get('county', '')}. Country: {address.get('country', '')}."
            return whereIam
        
        if zip:
            # return a string with zip code only
            location = geolocator.reverse(str(lat) + ", " + str(lon))
            whereIam = location.raw['address'].get('postcode', '')
            return whereIam
        
        if float(lat) == latitudeValue and float(lon) == longitudeValue:
            # redacted address when no GPS and using default location
            location = geolocator.reverse(str(lat) + ", " + str(lon))
            address = location.raw['address']
            address_components = {
                'city': 'City',
                'state': 'State',
                'postcode': 'Zip',
                'county': 'County',
                'country': 'Country'
            }
            whereIam += ', '.join([f"{label}: {address.get(component, '')}" for component, label in address_components.items() if component in address])
        else:
            location = geolocator.reverse(lat + ", " + lon)
            address = location.raw['address']
            address_components = {
                'house_number': 'Number',
                'road': 'Road',
                'city': 'City',
                'state': 'State',
                'postcode': 'Zip',
                'county': 'County',
                'country': 'Country'
            }
            whereIam += ', '.join([f"{label}: {address.get(component, '')}" for component, label in address_components.items() if component in address])
            whereIam += f", Grid: " + grid
        return whereIam
    except Exception as e:
        logger.debug("Location:Error fetching location data with whereami, likely network error")
        return ERROR_FETCHING_DATA
    
def getRepeaterBook(lat=0, lon=0):
    grid = mh.to_maiden(float(lat), float(lon))
    data = []
    repeater_url = f"https://www.repeaterbook.com/repeaters/prox_result.php?city={grid}&lat=&long=&distance=50&Dunit=m&band%5B%5D=4&band%5B%5D=16&freq=&call=&mode%5B%5D=1&mode%5B%5D=2&mode%5B%5D=4&mode%5B%5D=64&status_id=1&use=%25&use=OPEN&order=distance_calc%2C+state_id+ASC"
    try:
        msg = ''
        response = requests.get(repeater_url)
        soup = bs.BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', attrs={'class': 'w3-table w3-striped w3-responsive w3-mobile w3-auto sortable'})
        if table is not None:
            cells = table.find_all('td')
            data = []
            for i in range(0, len(cells), 11):
                if i + 10 < len(cells):  #avoid IndexError
                    repeater = {
                        'frequency': cells[i].text.strip() if i < len(cells) else 'N/A',
                        'offset': cells[i + 1].text.strip() if i + 1 < len(cells) else 'N/A',
                        'tone': cells[i + 2].text.strip() if i + 2 < len(cells) else 'N/A',
                        'call_sign': cells[i + 3].text.strip() if i + 3 < len(cells) else 'N/A',
                        'location': cells[i + 4].text.strip() if i + 4 < len(cells) else 'N/A',
                        'state': cells[i + 5].text.strip() if i + 5 < len(cells) else 'N/A',
                        'use': cells[i + 6].text.strip() if i + 6 < len(cells) else 'N/A',
                        'mode': cells[i + 7].text.strip() if i + 7 < len(cells) else 'N/A',
                        'distance': cells[i + 8].text.strip() if i + 8 < len(cells) else 'N/A',
                        'direction': cells[i + 9].text.strip() if i + 9 < len(cells) else 'N/A'
                    }
                    data.append(repeater)
                else:
                    msg = "bug?Not enough columns"
        else:
            msg = "bug?Table not found"
    except Exception as e:
        msg = "No repeaters found 😔"
    # Limit the output to the first 4 repeaters
    for repeater in data[:4]:
        tmpTone = repeater['tone'].replace(" /", "")
        msg += f"{repeater['call_sign']}📶{repeater['frequency']}{repeater['offset']},{tmpTone}.{repeater['mode']}"
        if repeater != data[:4][-1]: msg += '\n'
    return msg

def getArtSciRepeaters(lat=0, lon=0):
    # UK api_url = "https://api-beta.rsgb.online/all/systems"
    #grid = mh.to_maiden(float(lat), float(lon))
    repeaters = []
    zipCode = where_am_i(lat, lon, zip=True)
    if zipCode == NO_DATA_NOGPS or zipCode == ERROR_FETCHING_DATA:
        return zipCode

    if zipCode.isnumeric():
        try:
            artsci_url = f"http://www.artscipub.com/mobile/showstate.asp?zip={zipCode}"
            response = requests.get(artsci_url)
            soup = bs.BeautifulSoup(response.text, 'html.parser')
            # results needed xpath is /html/body/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table
            table = soup.find_all('table')[1]
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                # if no elements have the word 'located' then append
                if not any('located' in ele for ele in cols):
                    if not any('Location' in ele for ele in cols):
                        repeaters.append([ele for ele in cols if ele])
        except Exception as e:
            logger.error(f"Error fetching data from {artsci_url}: {e}")

    if repeaters != []:
        msg = f"Found:{len(repeaters)} in {zipCode}\n"
        for repeater in repeaters:
            # format is ['City', 'Frequency', 'Offset', 'PL', 'Call', 'Notes']
            # there might be missing elements or only one element
            if len(repeater) == 2:
                msg += f"Freq:{repeater[1]}"
            elif len(repeater) == 3:
                msg += f"Freq:{repeater[1]}, PL:{repeater[2]}"
            elif len(repeater) == 4:
                msg += f"Freq:{repeater[1]}, PL:{repeater[2]}, ID: {repeater[3]}"
            elif len(repeater) == 5:
                msg += f"Freq:{repeater[1]}, PL:{repeater[2]}, ID:{repeater[3]}"
            elif len(repeater) == 6:
                msg += f"Freq:{repeater[1]}, PL:{repeater[2]}, ID:{repeater[3]}. {repeater[5]}"
            if repeater != repeaters[-1]:
                msg += "\n"
    else:
        msg = f"no results.. sorry"
    return msg
    

def get_tide(lat=0, lon=0):
    station_id = ""
    if float(lat) == 0 and float(lon) == 0:
        logger.error("Location:No GPS data, try sending location for tide")
        return NO_DATA_NOGPS
    station_lookup_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/tidepredstations.json?lat=" + str(lat) + "&lon=" + str(lon) + "&radius=50"
    try:
        station_data = requests.get(station_lookup_url, timeout=urlTimeoutSeconds)
        if station_data.ok:
            station_json = station_data.json()
        else:
            logger.error("Location:Error fetching tide station table from NOAA")
            return ERROR_FETCHING_DATA
        
        if station_json['stationList'] == [] or station_json['stationList'] is None:
            logger.error("Location:No tide station found")
            return ERROR_FETCHING_DATA
        
        station_id = station_json['stationList'][0]['stationId']

    except (requests.exceptions.RequestException, json.JSONDecodeError):
        logger.error("Location:Error fetching tide station table from NOAA")
        return ERROR_FETCHING_DATA
    
    station_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=today&time_zone=lst_ldt&datum=MLLW&product=predictions&interval=hilo&format=json&station=" + station_id

    if use_metric:
        station_url += "&units=metric"
    else:
        station_url += "&units=english"

    try:
        tide_data = requests.get(station_url, timeout=urlTimeoutSeconds)
        if tide_data.ok:
            tide_json = tide_data.json()
        else:
            logger.error("Location:Error fetching tide data from NOAA")
            return ERROR_FETCHING_DATA

    except (requests.exceptions.RequestException, json.JSONDecodeError):
        logger.error("Location:Error fetching tide data from NOAA")
        return ERROR_FETCHING_DATA

    tide_data = tide_json['predictions']

    # format tide data into a table string for mesh
    # get the date out of the first t value 
    tide_date = tide_data[0]['t'].split(" ")[0]
    tide_table = "Tide Data for " + tide_date + "\n"
    for tide in tide_data:
        tide_time = tide['t'].split(" ")[1]
        if not zuluTime:
            # convert to 12 hour clock
            if int(tide_time.split(":")[0]) > 12:
                tide_time = str(int(tide_time.split(":")[0]) - 12) + ":" + tide_time.split(":")[1] + " PM"
            else:
                tide_time = tide_time + " AM"
                
        tide_table +=  tide['type'] + " " + tide_time + ", " + tide['v'] + "\n"
    # remove last newline
    tide_table = tide_table[:-1]
    return tide_table
    
def get_weather(lat=0, lon=0, unit=0):
    # get weather report from NOAA for forecast detailed
    weather = ""
    if float(lat) == 0 and float(lon) == 0:
        return NO_DATA_NOGPS
    
    # get weather data from NOAA units for metric unit = 1 is metric
    if use_metric:
        unit = 1
        
    weather_url = "https://forecast.weather.gov/MapClick.php?FcstType=text&lat=" + str(lat) + "&lon=" + str(lon)
    if unit == 1:
        weather_url += "&unit=1"
    
    try:
        weather_data = requests.get(weather_url, timeout=urlTimeoutSeconds)
        if not weather_data.ok:
            logger.error("Location:Error fetching weather data from NOAA")
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        logger.error("Location:Error fetching weather data from NOAA")
        return ERROR_FETCHING_DATA
    
    soup = bs.BeautifulSoup(weather_data.text, 'html.parser')
    table = soup.find('div', id="detailed-forecast-body")

    if table is None:
        logger.error("Location:Bad weather data from NOAA")
        return ERROR_FETCHING_DATA
    else:
        # get rows
        rows = table.find_all('div', class_="row")

    # extract data from rows
    for row in rows:
        # shrink the text
        line = abbreviate_noaa(row.text)
        # only grab a few days of weather
        if len(weather.split("\n")) < forecastDuration:
            weather += line + "\n"
    # trim off last newline
    weather = weather[:-1]

    # get any alerts and return the count
    alerts = getWeatherAlerts(lat, lon)

    if alerts == ERROR_FETCHING_DATA or alerts == NO_DATA_NOGPS or alerts == NO_ALERTS:
        alert = ""
        alert_num = 0
    else:
        alert = alerts[0]
        alert_num = alerts[1]

    if int(alert_num) > 0:
        # add the alert count warning to the weather
        weather = str(alert_num) + " local alerts!\n" + weather + "\n" + alert

    return weather

def abbreviate_noaa(row):
    # replace long strings with shorter ones for display
    replacements = {
        "monday": "Mon ",
        "tuesday": "Tue ",
        "wednesday": "Wed ",
        "thursday": "Thu ",
        "friday": "Fri ",
        "saturday": "Sat ",
        "sunday": "Sun ",
        "today": "Today ",
        "night": "Night ",
        "tonight": "Tonight ",
        "tomorrow": "Tomorrow ",
        "day": "Day ",
        "this afternoon": "Afternoon ",
        "overnight": "Overnight ",
        "northwest": "NW",
        "northeast": "NE",
        "southwest": "SW",
        "southeast": "SE",
        "north": "N",
        "south": "S",
        "east": "E",
        "west": "W",
        "precipitation": "precip",
        "showers": "shwrs",
        "thunderstorms": "t-storms",
        "thunderstorm": "t-storm",
        "quarters": "qtrs",
        "quarter": "qtr",
        "january": "Jan",
        "february": "Feb",
        "march": "Mar",
        "april": "Apr",
        "may": "May",
        "june": "Jun",
        "july": "Jul",
        "august": "Aug",
        "september": "Sep",
        "october": "Oct",
        "november": "Nov",
        "december": "Dec",
        "degrees": "°",
        "percent": "%",
        "department": "Dept.",
    }

    line = row
    for key, value in replacements.items():
        # case insensitive replace
        line = line.replace(key, value).replace(key.capitalize(), value).replace(key.upper(), value)
                    
    return line

def getWeatherAlerts(lat=0, lon=0, useDefaultLatLon=False):
    # get weather alerts from NOAA limited to ALERT_COUNT with the total number of alerts found
    alerts = ""
    if float(lat) == 0 and float(lon) == 0 and not useDefaultLatLon:
        return NO_DATA_NOGPS
    else:
        if useDefaultLatLon:
            lat = latitudeValue
            lon = longitudeValue

    alert_url = "https://api.weather.gov/alerts/active.atom?point=" + str(lat) + "," + str(lon)
    #alert_url = "https://api.weather.gov/alerts/active.atom?area=WA"
    #logger.debug("Location:Fetching weather alerts from NOAA for " + str(lat) + ", " + str(lon))
    
    try:
        alert_data = requests.get(alert_url, timeout=urlTimeoutSeconds)
        if not alert_data.ok:
            logger.warning("Location:Error fetching weather alerts from NOAA")
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        logger.warning("Location:Error fetching weather alerts from NOAA")
        return ERROR_FETCHING_DATA
    
    alerts = ""
    alertxml = xml.dom.minidom.parseString(alert_data.text)

    for i in alertxml.getElementsByTagName("entry"):
        alerts += (
            i.getElementsByTagName("title")[0].childNodes[0].nodeValue + "\n"
        )

    if alerts == "" or alerts == None:
        return NO_ALERTS

    # trim off last newline
    if alerts[-1] == "\n":
        alerts = alerts[:-1]
        
    # get the number of alerts
    alert_num = 0
    alert_num = len(alerts.split("\n"))

    alerts = abbreviate_noaa(alerts)

    # return the first ALERT_COUNT alerts
    data = "\n".join(alerts.split("\n")[:numWxAlerts]), alert_num
    return data

wxAlertCache = ""
def alertBrodcast():
    # get the latest weather alerts and broadcast them if there are any
    global wxAlertCache
    currentAlert = getWeatherAlerts(latitudeValue, longitudeValue)
    # check if any reason to discard the alerts
    if currentAlert == ERROR_FETCHING_DATA or currentAlert == NO_DATA_NOGPS:
        return False
    elif currentAlert == NO_ALERTS:
        wxAlertCache = ""
        return False
    # broadcast the alerts send to wxBrodcastCh
    elif currentAlert[0] != wxAlertCache:
        logger.debug("Location:Broadcasting weather alerts")
        wxAlertCache = currentAlert[0]
        return currentAlert
    
    return False

def getActiveWeatherAlertsDetail(lat=0, lon=0):
    # get the latest details of weather alerts from NOAA
    alerts = ""
    if float(lat) == 0 and float(lon) == 0:
        logger.warning("Location:No GPS data, try sending location for weather alerts")
        return NO_DATA_NOGPS

    alert_url = "https://api.weather.gov/alerts/active.atom?point=" + str(lat) + "," + str(lon)
    #alert_url = "https://api.weather.gov/alerts/active.atom?area=WA"
    #logger.debug("Location:Fetching weather alerts detailed from NOAA for " + str(lat) + ", " + str(lon))
    
    try:
        alert_data = requests.get(alert_url, timeout=urlTimeoutSeconds)
        if not alert_data.ok:
            logger.warning("Location:Error fetching weather alerts from NOAA")
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        logger.warning("Location:Error fetching weather alerts from NOAA")
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

    alerts = abbreviate_noaa(alerts)

    # trim the alerts to the first ALERT_COUNT
    alerts = alerts.split("\n***\n")[:numWxAlerts]
    
    if alerts == "" or alerts == ['']:
        return ERROR_FETCHING_DATA

    # trim off last newline
    if alerts[-1] == "\n":
        alerts = alerts[:-1]

    alerts = "\n".join(alerts)
    
    return alerts

def getIpawsAlert(lat=0, lon=0):
    # get the latest IPAWS alert from FEMA, untested code
    alert = ''
    alerts = []
    alert_url = "https://apps.fema.gov/IPAWSOPEN_EAS_SERVICE/rest/feed"
    try:
        alert_data = requests.get(alert_url, timeout=urlTimeoutSeconds)
        if not alert_data.ok:
            logger.warning("System: iPAWS fetching IPAWS alerts from FEMA")
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        logger.warning("System: iPAWS fetching IPAWS alerts from FEMA")
        return ERROR_FETCHING_DATA
    
    # main feed bulletins
    alertxml = xml.dom.minidom.parseString(alert_data.text)

    # extract alerts from main feed
    for entry in alertxml.getElementsByTagName("entry"):
        link = entry.getElementsByTagName("link")[0].getAttribute("href")
        try:
            linked_data = requests.get(link, timeout=urlTimeoutSeconds)
            if not linked_data.ok:
                #logger.warning(f"System: iPAWS Error fetching linked alert data from {link}")
                continue
        except (requests.exceptions.RequestException):
            logger.warning(f"System: iPAWS Error fetching embedded alert data from {link}")
            continue
        
        # this alert is a full CAP alert
        linked_xml = xml.dom.minidom.parseString(linked_data.text)

        for info in linked_xml.getElementsByTagName("info"):
            # extract values from XML
            eventCode_table = info.getElementsByTagName("eventCode")[0]
            alertType = eventCode_table.getElementsByTagName("valueName")[0].childNodes[0].nodeValue
            alertCode = eventCode_table.getElementsByTagName("value")[0].childNodes[0].nodeValue
            headline = info.getElementsByTagName("headline")[0].childNodes[0].nodeValue
            description = info.getElementsByTagName("description")[0].childNodes[0].nodeValue

            area_table = info.getElementsByTagName("area")[0]
            areaDesc = area_table.getElementsByTagName("areaDesc")[0].childNodes[0].nodeValue
            
            geocode_table = area_table.getElementsByTagName("geocode")[0]
            geocode_type = geocode_table.getElementsByTagName("valueName")[0].childNodes[0].nodeValue
            geocode_value = geocode_table.getElementsByTagName("value")[0].childNodes[0].nodeValue
            sameVal = "NONE"
            if geocode_type == "SAME":
                sameVal = geocode_value

            # comma separated list of SAME codes to trigger local alert. find yours https://www.weather.gov/nwr/counties
            mySAME = "053029","053073","004013"

            # if the alert is for the same area as the user add it to the alerts list
            if sameVal in mySAME:
                # add to alerts list
                alerts.append({
                    'alertType': alertType,
                    'alertCode': alertCode,
                    'headline': headline,
                    'areaDesc': areaDesc,
                    'geocode_type': geocode_type,
                    'geocode_value': geocode_value,
                    'description': description
                })
            else:
                print(f"Debug iPAWS: Type:{alertType} Code:{alertCode} Desc:{areaDesc} GeoType:{geocode_type} GeoVal:{geocode_value}, Headline:{headline}")
    
    # return the numWxAlerts of alerts
    if len(alerts) > 0:
        for alertItem in alerts[:numWxAlerts]:
            alert += abbreviate_noaa(f"🚨FEMA Alert: {alertItem['headline']}\n{alertItem['description']}")
            if alertItem != alerts[:numWxAlerts][-1]:
                alert += "\n"
    else:
        alert = NO_ALERTS

    return alert

