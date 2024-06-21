import unittest
from locationdata import *

class TestGetWeather(unittest.TestCase):
    def test_get_weather_with_valid_coordinates(self):
        # Test with valid coordinates
        lat = "37.7749"
        lon = "-122.4194"
        weather = get_weather(lat, lon)
        print(f"weather: {weather}")
        #self.assertNotEqual(weather, "no location data: does your device have GPS?")
        #self.assertNotEqual(weather, "error fetching weather data")

    def test_get_weather_with_invalid_coordinates(self):
        # Test with invalid coordinates
        lat = 0
        lon = 0
        weather = get_weather(lat, lon)
        print(f"weather: {weather}")
        #self.assertTrue("Today: " in weather)
        #self.assertTrue("Tonight: " in weather)

    def test_where_am_i_with_valid_coordinates(self):
        # Test with invalid coordinates
        lat = "37.7749"
        lon = "-122.4194"
        location = where_am_i(lat, lon)
        print(f"location: {location}")
        self.assertEqual(location, "South Van Ness Avenue San Francisco California 94103 United States Grid:CM87ss")

    def test_get_tide_with_valid_coordinates(self):
        # Test with valid coordinates
        lat = "37.7749"
        lon = "-122.4194"
        tide = get_tide(lat, lon)
        print(f"tide: {tide}")
        #self.assertNotEqual(tide, "no location data: does your device have GPS?")
        

if __name__ == '__main__':
    unittest.main()