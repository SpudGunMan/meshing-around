# helper functions to use location data for the API for NOAA weather, FEMA iPAWS, and repeater data
# K7MHI Kelly Keeton 2024

import json # pip install json
from geopy.geocoders import Nominatim # pip install geopy
import maidenhead as mh # pip install maidenhead
import requests # pip install requests
import bs4 as bs # pip install beautifulsoup4
import xml.dom.minidom 
from modules.log import *
import math


trap_list_location = ("whereami", "wx", "wxa", "wxalert", "rlist", "ea", "ealert", "riverflow", "valert", "earthquake", "howfar")

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
    # check if in the US or not
    usapi ="https://www.repeaterbook.com/repeaters/prox_result.php?"
    elsewhereapi = "https://www.repeaterbook.com/row_repeaters/prox2_result.php?"
    if grid[:2] in ['CN', 'DN', 'EN', 'FN', 'CM', 'DM', 'EM', 'FM', 'DL', 'EL', 'FL']:
        repeater_url = usapi
    else:
        repeater_url = elsewhereapi
    
    repeater_url += f"city={grid}&lat=&long=&distance=50&Dunit=m&band%5B%5D=4&band%5B%5D=16&freq=&call=&mode%5B%5D=1&mode%5B%5D=2&mode%5B%5D=4&mode%5B%5D=64&status_id=1&use=%25&use=OPEN&order=distance_calc%2C+state_id+ASC"
    
    try:
        msg = ''
        user_agent = {'User-agent': 'Mozilla/5.0'}
        response = requests.get(repeater_url, headers=user_agent, timeout=urlTimeoutSeconds)
        if response.status_code!=200:
            logger.error(f"Location:Error fetching repeater data from {repeater_url} with status code {response.status_code}")
        soup = bs.BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', attrs={'class': 'table table-striped table-hover align-middle sortable'})
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
            msg = "No Data for your Region"
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
            if response.status_code!=200:
                logger.error(f"Location:Error fetching data from {artsci_url} with status code {response.status_code}")
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

def get_NOAAtide(lat=0, lon=0):
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
            return "No tide station found with info provided"
        
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
    
def get_NOAAweather(lat=0, lon=0, unit=0):
    # get weather report from NOAA for forecast detailed
    weather = ""
    if float(lat) == 0 and float(lon) == 0:
        return NO_DATA_NOGPS
    
    # get weather data from NOAA units for metric unit = 1 is metric
    if use_metric:
        unit = 1
        logger.debug("Location: new API metric units not implemented yet")
        
    weather_url = "https://forecast.weather.gov/MapClick.php?FcstType=text&lat=" + str(lat) + "&lon=" + str(lon)
    weather_api = "https://api.weather.gov/points/" + str(lat) + "," + str(lon)
    # extract the "forecast": property from the JSON response
    try:
        weather_data = requests.get(weather_api, timeout=urlTimeoutSeconds)
        if not weather_data.ok:
            logger.warning("Location:Error fetching weather data from NOAA for location")
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        logger.warning("Location:Error fetching weather data from NOAA for location")
        return ERROR_FETCHING_DATA
    # get the forecast URL from the JSON response
    weather_json = weather_data.json()
    forecast_url = weather_json['properties']['forecast']
    try:
        forecast_data = requests.get(forecast_url, timeout=urlTimeoutSeconds)
        if not forecast_data.ok:
            logger.warning("Location:Error fetching weather forecast from NOAA")
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        logger.warning("Location:Error fetching weather forecast from NOAA")
        return ERROR_FETCHING_DATA
    
    # from periods, get the detailedForecast from number of days in NOAAforecastDuration
    forecast_json = forecast_data.json()
    forecast = forecast_json['properties']['periods']
    for day in forecast[:forecastDuration]:
        # abreviate the forecast

        weather += abbreviate_noaa(day['name']) + ": " + abbreviate_noaa(day['detailedForecast']) + "\n"
    # remove last newline
    weather = weather[:-1]

    # get any alerts and return the count
    alerts = getWeatherAlertsNOAA(lat, lon)

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
        "monday": "Mon",
        "tuesday": "Tue",
        "wednesday": "Wed",
        "thursday": "Thu",
        "friday": "Fri",
        "saturday": "Sat",
        "sunday": "Sun",
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
        "amounts less than a tenth of an inch possible.": "< 0.1in",
        "temperatures": "temps.",
        "temperature": "temp.",
    }

    line = row
    for key, value in replacements.items():
        # case insensitive replace
        line = line.replace(key, value).replace(key.capitalize(), value).replace(key.upper(), value)
                    
    return line

def getWeatherAlertsNOAA(lat=0, lon=0, useDefaultLatLon=False):
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
        title = i.getElementsByTagName("title")[0].childNodes[0].nodeValue
        area_desc = i.getElementsByTagName("cap:areaDesc")[0].childNodes[0].nodeValue
        if enableExtraLocationWx:
            alerts += f"{title}. {area_desc.replace(' ', '')}\n"
        else:
            alerts += f"{title}\n"

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

wxAlertCacheNOAA = ""
def alertBrodcastNOAA():
    # get the latest weather alerts and broadcast them if there are any
    global wxAlertCacheNOAA
    currentAlert = getWeatherAlertsNOAA(latitudeValue, longitudeValue)
    # check if any reason to discard the alerts
    if currentAlert == ERROR_FETCHING_DATA or currentAlert == NO_DATA_NOGPS:
        return False
    elif currentAlert == NO_ALERTS:
        wxAlertCacheNOAA = ""
        return False
    if ignoreEASenable:
        # check if the alert is in the ignoreEAS list
        for word in ignoreEASwords:
            if word.lower() in currentAlert[0].lower():
                logger.debug(f"Location:Ignoring NOAA Alert: {currentAlert[0]} containing {word}")
                return False
    # broadcast the alerts send to wxBrodcastCh
    elif currentAlert[0] not in wxAlertCacheNOAA:
        # Check if the current alert is not in the weather alert cache
        logger.debug("Location:Broadcasting weather alerts")
        wxAlertCacheNOAA = currentAlert[0]
        return currentAlert
    
    return False

def getActiveWeatherAlertsDetailNOAA(lat=0, lon=0):
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
        return NO_ALERTS

    # trim off last newline
    if alerts[-1] == "\n":
        alerts = alerts[:-1]

    alerts = "\n".join(alerts)
    
    return alerts

def getIpawsAlert(lat=0, lon=0, shortAlerts = False):
    # get the latest IPAWS alert from FEMA
    alert = ''
    alerts = []
    linked_data = ''
    
    # set the API URL for IPAWS
    namespace = "urn:oasis:names:tc:emergency:cap:1.2"
    alert_url = "https://apps.fema.gov/IPAWSOPEN_EAS_SERVICE/rest/feed"

    # get the alerts from FEMA
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

        ## state FIPS
        ## This logic is being added to reduce load on FEMA server.
        stateFips = None
        for cat in entry.getElementsByTagName("category"):
            if cat.getAttribute("label") == "statefips":
                stateFips = cat.getAttribute("term")
                break

        if stateFips is None:
            # no stateFIPS found — skip
            continue

        # check if it matches your list
        if stateFips not in myStateFIPSList:
            #logger.debug(f"Skipping FEMA record link {link} with stateFIPS code of: {stateFips} because it doesn't match our StateFIPSList {myStateFIPSList}")
            continue  # skip to next entry

        try:
            # get the linked alert data from FEMA
            linked_data = requests.get(link, timeout=urlTimeoutSeconds)
            if not linked_data.ok or not linked_data.text.strip():
                # if the linked data is not ok, skip this alert
                #logger.warning(f"System: iPAWS Error fetching linked alert data from {link}")
                continue
            else:
                linked_xml = xml.dom.minidom.parseString(linked_data.text)
                # this alert is a full CAP alert
        except (requests.exceptions.RequestException):
            logger.warning(f"System: iPAWS Error fetching embedded alert data from {link}")
            continue
        except xml.parsers.expat.ExpatError:
            logger.warning(f"System: iPAWS Error parsing XML from {link}")
            continue
        except Exception as e:
            logger.debug(f"System: iPAWS Error processing alert data from {link}: {e}")
            continue

        for info in linked_xml.getElementsByTagName("info"):
            # only get en-US language alerts (alternative is es-US)
            language_nodes = info.getElementsByTagName("language")
            if not any(node.firstChild and node.firstChild.nodeValue.strip() == "en-US" for node in language_nodes):
                    continue  # skip if not en-US
            # extract values from XML
            sameVal = "NONE"
            geocode_value = "NONE"
            description = ""
            try:
                eventCode_table = info.getElementsByTagName("eventCode")[0]
                alertType = eventCode_table.getElementsByTagName("valueName")[0].childNodes[0].nodeValue
                alertCode = eventCode_table.getElementsByTagName("value")[0].childNodes[0].nodeValue
                headline = info.getElementsByTagName("headline")[0].childNodes[0].nodeValue
                # use headline if no description
                if info.getElementsByTagName("description") and info.getElementsByTagName("description")[0].childNodes:
                    description = info.getElementsByTagName("description")[0].childNodes[0].nodeValue
                else:
                    description = headline

                area_table = info.getElementsByTagName("area")[0]
                areaDesc = area_table.getElementsByTagName("areaDesc")[0].childNodes[0].nodeValue
                geocode_table = area_table.getElementsByTagName("geocode")[0]
                geocode_type = geocode_table.getElementsByTagName("valueName")[0].childNodes[0].nodeValue
                geocode_value = geocode_table.getElementsByTagName("value")[0].childNodes[0].nodeValue
                if geocode_type == "SAME":
                    sameVal = geocode_value
                
            except Exception as e:
                logger.debug(f"System: iPAWS Error extracting alert data: {link}")
                #print(f"DEBUG: {info.toprettyxml()}")
                continue

             # check if the alert is for the SAME location, if wanted keep alert
            if (sameVal in mySAMEList) or (geocode_value in mySAMEList) or mySAMEList == ['']:
                # ignore the FEMA test alerts
                if ignoreFEMAenable:
                    ignore_alert = False
                    for word in ignoreFEMAwords:
                        if word.lower() in headline.lower():
                            logger.debug(f"System: Filtering FEMA Alert by WORD: {headline} containing {word} at {areaDesc}")
                            ignore_alert = True
                            break
                if ignore_alert:
                    continue

                # add to alert list
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
                logger.debug(f"System: iPAWS Alert not in SAME List: {sameVal} or {geocode_value} for {headline} at {areaDesc}")
                continue

    # return the numWxAlerts of alerts
    if len(alerts) > 0:
        for alertItem in alerts[:numWxAlerts]:
            if shortAlerts:
                alert += abbreviate_noaa(f"🚨FEMA Alert: {alertItem['headline']}")
            else:
                alert += abbreviate_noaa(f"🚨FEMA Alert: {alertItem['headline']}\n{alertItem['description']}")
            # add a newline if not the last alert    
            if alertItem != alerts[:numWxAlerts][-1]:
                alert += "\n"
    else:
        alert = NO_ALERTS

    return alert

def get_flood_noaa(lat=0, lon=0, uid=0):
    # get the latest flood alert from NOAA
    api_url = "https://api.water.noaa.gov/nwps/v1/gauges/"
    headers = {'accept': 'application/json'}
    if uid == 0:
        return "No flood gauge data found"
    try:
        response = requests.get(api_url + str(uid), headers=headers, timeout=urlTimeoutSeconds)
        if not response.ok:
            logger.warning("Location:Error fetching flood gauge data from NOAA for " + str(uid))
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        logger.warning("Location:Error fetching flood gauge data from NOAA for " + str(uid))
        return ERROR_FETCHING_DATA
    
    data = response.json()
    if not data:
        return "No flood gauge data found"
    
    # extract values from JSON
    try:
        name = data['name']
        status_observed_primary = data['status']['observed']['primary']
        status_observed_primary_unit = data['status']['observed']['primaryUnit']
        status_observed_secondary = data['status']['observed']['secondary']
        status_observed_secondary_unit = data['status']['observed']['secondaryUnit']
        status_observed_floodCategory = data['status']['observed']['floodCategory']
        status_forecast_primary = data['status']['forecast']['primary']
        status_forecast_primary_unit = data['status']['forecast']['primaryUnit']
        status_forecast_secondary = data['status']['forecast']['secondary']
        status_forecast_secondary_unit = data['status']['forecast']['secondaryUnit']
        status_forecast_floodCategory = data['status']['forecast']['floodCategory']

        # except KeyError as e:
        #     print(f"Missing key in data: {e}")
        # except TypeError as e:
        #     print(f"Type error in data: {e}")
    except Exception as e:
        logger.debug("Location:Error extracting flood gauge data from NOAA for " + str(uid))
        return ERROR_FETCHING_DATA
    
    # format the flood data
    logger.debug(f"System: NOAA Flood data for {str(uid)}")
    flood_data = f"Flood Data {name}:\n"
    flood_data += f"Observed: {status_observed_primary}{status_observed_primary_unit}({status_observed_secondary}{status_observed_secondary_unit}) risk: {status_observed_floodCategory}"
    flood_data += f"\nForecast: {status_forecast_primary}{status_forecast_primary_unit}({status_forecast_secondary}{status_forecast_secondary_unit}) risk: {status_forecast_floodCategory}"

    return flood_data

def get_volcano_usgs(lat=0, lon=0):
    alerts = ''
    if lat == 0 and lon == 0:
        lat = latitudeValue
        lon = longitudeValue
    # get the latest volcano alert from USGS from CAP feed
    usgs_volcano_url = "https://volcanoes.usgs.gov/hans-public/api/volcano/getCapElevated"
    try:
        volcano_data = requests.get(usgs_volcano_url, timeout=urlTimeoutSeconds)
        if not volcano_data.ok:
            logger.warning("System: Issue with fetching volcano alerts from USGS")
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        logger.warning("System: Issue with fetching volcano alerts from USGS")
        return ERROR_FETCHING_DATA
    volcano_json = volcano_data.json()
    # extract alerts from main feed
    if volcano_json and isinstance(volcano_json, list):
        for alert in volcano_json:
            # check ignore list
            if ignoreUSGSEnable:
                for word in ignoreUSGSwords:
                    if word.lower() in alert['volcano_name_appended'].lower():
                        logger.debug(f"System: Ignoring USGS Alert: {alert['volcano_name_appended']} containing {word}")
                        continue
            # check if the alert lat long is within the range of bot latitudeValue and longitudeValue
            if (alert['latitude'] >= latitudeValue - 10 and alert['latitude'] <= latitudeValue + 10) and (alert['longitude'] >= longitudeValue - 10 and alert['longitude'] <= longitudeValue + 10):
                volcano_name = alert['volcano_name_appended']
                alert_level = alert['alert_level']
                color_code = alert['color_code']
                cap_severity = alert['cap_severity']
                synopsis = alert['synopsis']
                # format Alert
                alerts += f"🌋🚨: {volcano_name}, {alert_level} {color_code}, {cap_severity}.\n{synopsis}\n"
            else:
                #logger.debug(f"System: USGS volcano alert not in range: {alert['volcano_name_appended']}")
                continue
    else:
        logger.debug("Location:Error fetching volcano data from USGS")
        return NO_ALERTS
    if alerts == "":
        return NO_ALERTS
    # trim off last newline
    if alerts[-1] == "\n":
        alerts = alerts[:-1]
    # return the alerts
    alerts = abbreviate_noaa(alerts)
    return alerts

def get_nws_marine(zone, days=3):
    # forcast from NWS coastal products
    try:
        marine_pz_data = requests.get(zone, timeout=urlTimeoutSeconds)
        if not marine_pz_data.ok:
            logger.warning("Location:Error fetching NWS Marine PZ data")
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        logger.warning("Location:Error fetching NWS Marine PZ data")
        return ERROR_FETCHING_DATA
    
    marine_pz_data = marine_pz_data.text
    #validate data
    todayDate = today.strftime("%Y%m%d")
    if marine_pz_data.startswith("Expires:"):
        expires = marine_pz_data.split(";;")[0].split(":")[1]
        expires_date = expires[:8]
        if expires_date < todayDate:
            logger.debug("Location: NWS Marine PZ data expired")
            return ERROR_FETCHING_DATA
    else:
        logger.debug("Location: NWS Marine PZ data not valid")
        return ERROR_FETCHING_DATA
    
    # process the marine forecast data
    marine_pzz_lines = marine_pz_data.split("\n")
    marine_pz_report = ""
    day_blocks = []
    current_block = ""
    in_forecast = False

    for line in marine_pzz_lines:
        if line.startswith(".") and "..." in line:
            in_forecast = True
            if current_block:
                day_blocks.append(current_block.strip())
                current_block = ""
            current_block += line.strip() + " "
        elif in_forecast and line.strip() != "":
            current_block += line.strip() + " "
    if current_block:
        day_blocks.append(current_block.strip())

    # Only keep up to pzDays blocks
    for block in day_blocks[:days]:
        marine_pz_report += block + "\n"

    # remove last newline
    if marine_pz_report.endswith("\n"):
        marine_pz_report = marine_pz_report[:-1]

    # remove NOAA EOF $$
    if marine_pz_report.endswith("$$"):
        marine_pz_report = marine_pz_report[:-2].strip()

    # abbreviate the report
    marine_pz_report = abbreviate_noaa(marine_pz_report)
    if marine_pz_report == "":
        return NO_DATA_NOGPS
    return marine_pz_report

def checkUSGSEarthQuake(lat=0, lon=0):
    if lat == 0 and lon == 0:
        lat = latitudeValue
        lon = longitudeValue
    radius = 100 # km
    magnitude = 1.5
    history = 7 # days
    startDate = datetime.fromtimestamp(datetime.now().timestamp() - history*24*60*60).strftime("%Y-%m-%d")
    USGSquake_url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?&format=xml&latitude={lat}&longitude={lon}&maxradiuskm={radius}&minmagnitude={magnitude}&starttime={startDate}"
    description_text = ""
    quake_count = 0
    # fetch the earthquake data from USGS
    try:
        quake_data = requests.get(USGSquake_url, timeout=urlTimeoutSeconds)
        if not quake_data.ok:
            logger.warning("Location:Error fetching earthquake data from USGS")
            return NO_ALERTS
        if not quake_data.text.strip():
            return NO_ALERTS
        try:
            quake_xml = xml.dom.minidom.parseString(quake_data.text)
        except Exception as e:
            logger.warning(f"Location: USGS earthquake API returned invalid XML: {e}")
            return NO_ALERTS
    except (requests.exceptions.RequestException):
        logger.warning("Location:Error fetching earthquake data from USGS")
        return NO_ALERTS

    quake_xml = xml.dom.minidom.parseString(quake_data.text)
    quake_count = len(quake_xml.getElementsByTagName("event"))

    #get largest mag in magnitude of the set of quakes
    largest_mag = 0.0
    for event in quake_xml.getElementsByTagName("event"):
        mag = event.getElementsByTagName("magnitude")[0]
        mag_value = float(mag.getElementsByTagName("value")[0].childNodes[0].nodeValue)
        if mag_value > largest_mag:
            largest_mag = mag_value
            # set description text
            description_text = event.getElementsByTagName("description")[0].getElementsByTagName("text")[0].childNodes[0].nodeValue
    largest_mag = round(largest_mag, 1)
    if quake_count == 0:
        return NO_ALERTS
    else:
        return f"{quake_count} 🫨quakes in last {history} days within {radius} km. Largest: {largest_mag}M\n{description_text}"


howfarDB = {}
def distance(lat=0,lon=0,nodeID=0, reset=False):
    # part of the howfar function, calculates the distance between two lat/lon points
    msg = ""
    dupe = False
    r = 6371 # Radius of earth in kilometers # haversine formula
    
    if lat == 0 and lon == 0:
        return NO_DATA_NOGPS
    if nodeID == 0:
        return "No NodeID provided"
    
    if reset:
        if nodeID in howfarDB:
            del howfarDB[nodeID]
    
    if nodeID not in howfarDB:
        #register first point NodeID, lat, lon, time, point
        howfarDB[nodeID] = [{'lat': lat, 'lon': lon, 'time': datetime.now()}]
        if reset:
            return "Tracking reset, new starting point registered🗺️"
        else:
            return "Starting point registered🗺️"
    else:
        #de-dupe points if same as last point
        if howfarDB[nodeID][-1]['lat'] == lat and howfarDB[nodeID][-1]['lon'] == lon:
            dupe = True
            msg = "No New GPS📍 "
        # calculate distance from last point in howfarDB
        last_point = howfarDB[nodeID][-1]
        lat1 = math.radians(last_point['lat'])
        lon1 = math.radians(last_point['lon'])
        lat2 = math.radians(lat)
        lon2 = math.radians(lon)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))

        distance_km = c * r
        if use_metric:
            msg += f"{distance_km:.2f} km"
        else:
            distance_miles = distance_km * 0.621371
            msg += f"{distance_miles:.2f} miles"
        
        #calculate bearing
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        msg += f" 🧭{compass_bearing:.2f}° Bearing from last📍"

        # calculate the speed if time difference is more than 1 minute
        time_diff = datetime.now() - last_point['time']
        if time_diff.total_seconds() > 60:
            hours = time_diff.total_seconds() / 3600
            if use_metric:
                speed = distance_km / hours
                speed_str = f"{speed:.2f} km/h"
            else:
                speed_mph = (distance_km * 0.621371) / hours
                speed_str = f"{speed_mph:.2f} mph"
            msg += f", travel time: {int(time_diff.total_seconds()//60)} min, Speed: {speed_str}"

        # calculate total distance traveled including this point computed in distance_km from calculate distance from last point in howfarDB
        total_distance_km = 0.0
        for i in range(1, len(howfarDB[nodeID])):
            point1 = howfarDB[nodeID][i-1]
            point2 = howfarDB[nodeID][i]
            lat1 = math.radians(point1['lat'])
            lon1 = math.radians(point1['lon'])
            lat2 = math.radians(point2['lat'])
            lon2 = math.radians(point2['lon'])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
            c = 2 * math.asin(math.sqrt(a))
            total_distance_km += c * r
        # add the distance from last point to current point
        total_distance_km += distance_km
        if use_metric:
            msg += f", Total: {total_distance_km:.2f} km"
        else:
            total_distance_miles = total_distance_km * 0.621371
            msg += f", Total: {total_distance_miles:.2f} miles"
        
        # update the last point in howfarDB
        if not dupe:
            howfarDB[nodeID].append({'lat': lat, 'lon': lon, 'time': datetime.now()})
        
        # if points 3+ are within 30 meters of the first point add the area of the polygon
        if len(howfarDB[nodeID]) >= 3:
            points = []
            # loop the howfarDB to get all the points except the current nodeID
            for key in howfarDB:
                if key != nodeID:
                    points.append((howfarDB[key][-1]['lat'], howfarDB[key][-1]['lon']))
            # loop the howfarDB[nodeID] to get the points
            for point in howfarDB[nodeID]:
                points.append((point['lat'], point['lon']))
            # close the polygon by adding the first point to the end
            points.append((howfarDB[nodeID][0]['lat'], howfarDB[nodeID][0]['lon']))
            # calculate the area of the polygon
            area = 0.0
            for i in range(len(points)-1):
                lat1 = math.radians(points[i][0])
                lon1 = math.radians(points[i][1])
                lat2 = math.radians(points[i+1][0])
                lon2 = math.radians(points[i+1][1])
                area += (lon2 - lon1) * (2 + math.sin(lat1) + math.sin(lat2))
            area = area * (6378137 ** 2) / 2.0
            area = abs(area) / 1e6 # convert to square kilometers

            if use_metric:
                msg += f", Area: {area:.2f} sq.km (approx)"
            else:
                area_miles = area * 0.386102
                msg += f", Area: {area_miles:.2f} sq.mi (approx)"
            
            #calculate the centroid of the polygon
            x = 0.0
            y = 0.0
            z = 0.0
            for point in points[:-1]:
                lat_rad = math.radians(point[0])
                lon_rad = math.radians(point[1])
                x += math.cos(lat_rad) * math.cos(lon_rad)
                y += math.cos(lat_rad) * math.sin(lon_rad)
                z += math.sin(lat_rad)
            total_points = len(points) - 1
            x /= total_points
            y /= total_points
            z /= total_points
            lon_centroid = math.atan2(y, x)
            hyp = math.sqrt(x * x + y * y)
            lat_centroid = math.atan2(z, hyp)
            lat_centroid = math.degrees(lat_centroid)
            lon_centroid = math.degrees(lon_centroid)
            msg += f", Centroid: {lat_centroid:.5f}, {lon_centroid:.5f}"

        return msg

def get_openskynetwork(lat=0, lon=0):
    # get the latest aircraft data from OpenSky Network in the area
    if lat == 0 and lon == 0:
        return NO_ALERTS
    # setup a bounding box of 50km around the lat/lon
    box_size = 0.45 # approx 50km
    # return limits for aircraft search
    search_limit = 3
    lamin = lat - box_size
    lamax = lat + box_size
    lomin = lon - box_size
    lomax = lon + box_size

    # fetch the aircraft data from OpenSky Network
    opensky_url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
    try:
        aircraft_data = requests.get(opensky_url, timeout=urlTimeoutSeconds)
        if not aircraft_data.ok:
            logger.warning("Location:Error fetching aircraft data from OpenSky Network")
            return ERROR_FETCHING_DATA
    except (requests.exceptions.RequestException):
        logger.warning("Location:Error fetching aircraft data from OpenSky Network")
        return ERROR_FETCHING_DATA
    aircraft_json = aircraft_data.json()
    if 'states' not in aircraft_json or not aircraft_json['states']:
        return NO_ALERTS
    aircraft_list = aircraft_json['states']
    aircraft_report = ""
    for aircraft in aircraft_list:
        if len(aircraft_report.split("\n")) >= search_limit:
            break
        # extract values from JSON
        try:
            callsign = aircraft[1].strip() if aircraft[1] else "N/A"
            origin_country = aircraft[2]
            velocity = aircraft[9]
            true_track = aircraft[10]
            vertical_rate = aircraft[11]
            sensors = aircraft[12]
            geo_altitude = aircraft[13]
            squawk = aircraft[14] if len(aircraft) > 14 else "N/A"
        except Exception as e:
            logger.debug("Location:Error extracting aircraft data from OpenSky Network")
            continue
        
        # format the aircraft data
        aircraft_report += f"{callsign} Alt:{int(geo_altitude) if geo_altitude else 'N/A'}m Vel:{int(velocity) if velocity else 'N/A'}m/s Heading:{int(true_track) if true_track else 'N/A'}°\n"
    
    # remove last newline
    if aircraft_report.endswith("\n"):
        aircraft_report = aircraft_report[:-1]
    aircraft_report = abbreviate_noaa(aircraft_report)
    return aircraft_report if aircraft_report else NO_ALERTS
