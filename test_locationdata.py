import unittest
from locationdata import get_weather

class TestGetWeather(unittest.TestCase):
    def test_get_weather_with_valid_coordinates(self):
        # Test with valid coordinates
        lat = 37.7749
        lon = -122.4194
        weather = get_weather(lat, lon)
        print(weather)
        self.assertNotEqual(weather, "no location data: does your device have GPS?")
        #self.assertNotEqual(weather, "error fetching weather data")

    def test_get_weather_with_invalid_coordinates(self):
        # Test with invalid coordinates
        lat = 0
        lon = 0
        weather = get_weather(lat, lon)
        print(weather)
        #self.assertTrue("Today: " in weather)
        #self.assertTrue("Tonight: " in weather)

if __name__ == '__main__':
    unittest.main()