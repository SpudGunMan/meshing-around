# helper functions to use location data
# K7MHI Kelly Keeton 2024

from geopy.geocoders import Nominatim # pip install geopy
import maidenhead as mh # pip install maidenhead
import requests # pip install requests

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
    station_lookup_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?lat=" + lat + "&lon=" + lon + "&radius=30"
    station_data = requests.get(station_lookup_url, timeout=5)
    if(station_data.ok):
        station_json = station_data.json()
        print(station_json)
        station_id = station_json['stationList'][0]['stationId']
    else:
        return "error fetching station data"

    return "tide data"