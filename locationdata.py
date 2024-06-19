# helper functions to use location data
# K7MHI Kelly Keeton 2024

from geopy.geocoders import Nominatim # pip install geopy
import maidenhead as mh # pip install maidenhead

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
    print(whereIam)
    print(lat, lon)
    whereIam += " Grid: " + mh.to_maiden(lat,lon,6)
    
    return whereIam