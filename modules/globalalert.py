# helper functions to use location data for data outside US/north america
# K7MHI Kelly Keeton 2024

import json # pip install json
#from geopy.geocoders import Nominatim # pip install geopy
#import maidenhead as mh # pip install maidenhead
import requests # pip install requests
import bs4 as bs # pip install beautifulsoup4
#import xml.dom.minidom 
from modules.log import logger
from modules.settings import urlTimeoutSeconds, NO_ALERTS, myRegionalKeysDE

trap_list_location_eu = ("ukalert")
trap_list_location_de = ("dealert")

def get_govUK_alerts(lat, lon):
    try:
        # get UK.gov alerts
        url = 'https://www.gov.uk/alerts'
        response = requests.get(url, timeout=urlTimeoutSeconds)
        soup = bs.BeautifulSoup(response.text, 'html.parser')
        # the alerts are in <h2 class="govuk-heading-m" id="alert-status">
        alert = soup.find('h2', class_='govuk-heading-m', id='alert-status')
    except Exception as e:
        logger.warning("Error getting UK alerts: " + str(e))
        return 
    
    if alert:
        return "🚨" + alert.get_text(strip=True)
    else:
        return NO_ALERTS

def get_nina_alerts():
    try:
        # get api.bund.dev alerts
        alerts = []
        for regionalKey in myRegionalKeysDE:
            url = ("https://nina.api.proxy.bund.dev/api31/dashboard/" + regionalKey + ".json")
            response = requests.get(url, timeout=urlTimeoutSeconds)
            data = response.json()

            for item in data:
                title = item["i18nTitle"]["de"]
                alerts.append(f"🚨 {title}")
        return "\n".join(alerts) if alerts else NO_ALERTS
    except Exception as e:
        logger.warning("Error getting NINA DE alerts: " + str(e))
        return NO_ALERTS

def get_wxUKgov():
    # get UK weather warnings, these look icky
    url = 'https://www.metoffice.gov.uk/weather/guides/rss'
    url = 'https://www.metoffice.gov.uk/public/data/PWSCache/WarningsRSS/Region/nw'
    try:
        # get UK weather warnings
        url = 'https://www.metoffice.gov.uk/weather/guides/rss'
        response = requests.get(url, timeout=urlTimeoutSeconds)
        soup = bs.BeautifulSoup(response.content, 'xml')
        
        items = soup.find_all('item')
        alerts = []
        
        for item in items:
            title = item.find('title').get_text(strip=True)
            description = item.find('description').get_text(strip=True)
            alerts.append(f"🚨 {title}: {description}")
        
        return "\n".join(alerts) if alerts else NO_ALERTS
    except Exception as e:
        logger.warning("Error getting UK weather warnings: " + str(e))
        return NO_ALERTS
    
    
def get_floodUKgov():
    # get UK flood warnings, there is so much I need a locals help
    url = 'https://environment.data.gov.uk/flood-widgets/rss/feed-England.xml'
    
    return NO_ALERTS

def get_crimeUKgov(lat, lon):
    """
    Fetches recent street crime data from UK Police API for given lat/lon.
    Returns a summary string or NO_ALERTS. -- pay for use?
    """
    date = datetime.datetime.now().strftime("%Y-%m")
    url = f'https://data.police.uk/api/crimes-street/all-crime?date={date}&lat={lat}&lng={lon}'
    try:
        response = requests.get(url, timeout=urlTimeoutSeconds)
        if not response.ok or not response.text.strip():
            return NO_ALERTS
        crimes = response.json()
        if not crimes:
            return NO_ALERTS
        # Summarize the first few crimes
        summaries = []
        for crime in crimes[:3]:
            category = crime.get("category", "Unknown")
            outcome = crime.get("outcome_status", {}).get("category", "No outcome")
            location = crime.get("location", {}).get("street", {}).get("name", "Unknown location")
            summaries.append(f"{category.title()} at {location} ({outcome})")
        return "\n".join(summaries)
    except Exception as e:
        logger.warning(f"Error fetching UK crime data: {e}")
        return NO_ALERTS

def get_crime_stopsUKgov(lat, lon):
    """
    Fetches recent stop-and-search data from UK Police API for given lat/lon.
    Returns a summary string or NO_ALERTS. -- pay for use?
    """
    date = datetime.datetime.now().strftime("%Y-%m")
    url = f'https://data.police.uk/api/stops-street?date={date}&lat={lat}&lng={lon}'
    try:
        response = requests.get(url, timeout=urlTimeoutSeconds)
        if not response.ok or not response.text.strip():
            return NO_ALERTS
        stops = response.json()
        if not stops:
            return NO_ALERTS
        # Summarize the first few stops
        summaries = []
        for stop in stops[:3]:  # Limit to first 3 stops for brevity
            summary = (
                f"Date: {stop.get('datetime', 'N/A')}, "
                f"Outcome: {stop.get('outcome', 'N/A')}, "
                f"Ethnicity: {stop.get('self_defined_ethnicity', 'N/A')}, "
                f"Gender: {stop.get('gender', 'N/A')}, "
                f"Location: {stop.get('location', {}).get('street', {}).get('name', 'N/A')}"
            )
            summaries.append(summary)
        return "\n".join(summaries)
    except Exception as e:
        return NO_ALERTS
