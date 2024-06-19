# helper functions to use location data
# K7MHI Kelly Keeton 2024

from geopy.geocoders import Nominatim # pip install geopy

def where_am_i(lat=0, lon=0):
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="mesh-bot")
    
    location = geolocator.reverse(lat+","+lon)
    address = location.raw['address']

    return address