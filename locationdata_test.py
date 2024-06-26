import unittest
from locationdata import *

class TestGetWeather(unittest.TestCase):

    def test_get_weather_with_valid_coordinates(self):
        # Test with valid coordinates
        lat = "37.7749"
        lon = "-122.4194"
        weather = get_weather(lat, lon)
        print(f"weather: {weather}")
        self.assertNotEqual(weather, NO_DATA_NOGPS)
        self.assertNotEqual(weather, ERROR_FETCHING_DATA)

    def test_get_weather_with_invalid_coordinates(self):
        # Test with invalid coordinates
        lat = 0
        lon = 0
        weather = get_weather(lat, lon)
        print(f"weather: {weather}")
        self.assertEqual(weather, NO_DATA_NOGPS)

    def test_where_am_i_with_valid_coordinates(self):
        # Test with invalid coordinates
        lat = "37.7749"
        lon = "-122.4194"
        location = where_am_i(lat, lon)
        print(f"location: {location}")
        self.assertEqual(location, "South Van Ness Avenue San Francisco California 94103 United States Grid: CM87ss")
        self.assertNotEqual(location, NO_DATA_NOGPS)
        self.assertNotEqual(location, ERROR_FETCHING_DATA)

    def test_get_tide_with_valid_coordinates(self):
        # Test with valid coordinates
        lat = "37.7749"
        lon = "-122.4194"
        tide = get_tide(lat, lon)
        print(f"tide: {tide}")
        self.assertNotEqual(tide, NO_DATA_NOGPS)
        self.assertNotEqual(tide, ERROR_FETCHING_DATA)
        

if __name__ == '__main__':
    unittest.main()