# helper functions to use location data
# K7MHI Kelly Keeton 2024

from geopy.geocoders import Nominatim # pip install geopy
import maidenhead as mh # pip install maidenhead
import requests # pip install requests
import bs4 as bs # pip install beautifulsoup4

def where_am_i(lat=0, lon=0):
    whereIam = ""
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="mesh-bot")
    
    location = geolocator.reverse(lat+","+lon)
    address = location.raw['address']
    if 'house_number' in address:
        whereIam += address['house_number'] + " "
    if 'road' in address:
        whereIam += address['road'] + ", "
    if 'city' in address:
        whereIam += address['city'] + ", "
    if 'state' in address:
        whereIam += address['state'] + " "
    if 'postcode' in address:
        whereIam += address['postcode']
    if 'county' in address:
        whereIam += " " + address['county']
    if 'country' in address:
        whereIam += " " + address['country']
    grid = mh.to_maiden(float(lat), float(lon))
    whereIam += " Grid:" + grid
    
    return whereIam

def get_tide(lat=0, lon=0):
    station_id = ""
    if int(lat) == 0 and int(lon) == 0:
        return "error: no location data"
    station_lookup_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/tidepredstations.json?lat=" + str(lat) + "&lon=" + str(lon) + "&radius=50"
    station_data = requests.get(station_lookup_url, timeout=5)
    if(station_data.ok):
        station_json = station_data.json()
        #get first station id in 50 mile radius
        station_id = station_json['stationList'][0]['stationId']

    station_url="https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id="+station_id
    station_data = requests.get(station_url, timeout=5)
    if(station_data.ok):
        #extract table class="table table-condensed"
        soup = bs.BeautifulSoup(station_data.text, 'html.parser')
        table = soup.find('table', class_='table table-condensed')

        #extract rows
        rows = table.find_all('tr')
        #extract data from rows
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
        #trim off last newline
        tide_string = tide_string[:-1]
        return tide_string
                 
    else:
        return "error fetching tide data"
