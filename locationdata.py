# helper functions to use location data
# K7MHI Kelly Keeton 2024

from geopy.geocoders import Nominatim # pip install geopy

def where_am_i(lat=0, lon=0):
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="geoapiExercises")
    
    location = geolocator.reverse(lat+","+lon)
    address = location.raw['address']
    
    # traverse the data
    city = address.get('city', '')
    state = address.get('state', '')
    country = address.get('country', '')
    zipcode = address.get('postcode')
    print('City : ', city)
    print('State : ', state)
    print('Country : ', country)
    print('Zip Code : ', zipcode)

    return location