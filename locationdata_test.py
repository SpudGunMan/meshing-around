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
        # test replacement works
        self.assertNotIn(weather, "Sunday")
        self.assertNotIn(weather, "Monday")
        self.assertNotIn(weather, "Tuesday")
        self.assertNotIn(weather, "Wednesday")
        self.assertNotIn(weather, "Thursday")
        self.assertNotIn(weather, "Friday")
        self.assertNotIn(weather, "Saturday")
        self.assertNotIn(weather, "northwest")
        self.assertNotIn(weather, "northeast")
        self.assertNotIn(weather, "southwest")
        self.assertNotIn(weather, "southeast")
        self.assertNotIn(weather, "north")
        self.assertNotIn(weather, "south")
        self.assertNotIn(weather, "east")
        self.assertNotIn(weather, "west")
        self.assertNotIn(weather, "precipitation")
        self.assertNotIn(weather, "showers")
        self.assertNotIn(weather, "thunderstorms")
        
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

    def test_replace_weather(self):
        # Test replacing days of the week
        self.assertEqual(replace_weather("Monday"), "Mon ")
        self.assertEqual(replace_weather("Tuesday"), "Tue ")
        self.assertEqual(replace_weather("Wednesday"), "Wed ")
        self.assertEqual(replace_weather("Thursday"), "Thu ")
        self.assertEqual(replace_weather("Friday"), "Fri ")
        self.assertEqual(replace_weather("Saturday"), "Sat ")
        
        # Test replacing time periods
        self.assertEqual(replace_weather("Today"), "Today ")
        self.assertEqual(replace_weather("Tonight"), "Tonight ")
        self.assertEqual(replace_weather("Tomorrow"), "Tomorrow ")
        self.assertEqual(replace_weather("This Afternoon"), "Afternoon ")
        
        # Test replacing directions
        self.assertEqual(replace_weather("northwest"), "NW")
        self.assertEqual(replace_weather("northeast"), "NE")
        self.assertEqual(replace_weather("southwest"), "SW")
        self.assertEqual(replace_weather("southeast"), "SE")
        self.assertEqual(replace_weather("north"), "N")
        self.assertEqual(replace_weather("south"), "S")
        self.assertEqual(replace_weather("east"), "E")
        self.assertEqual(replace_weather("west"), "W")
        self.assertEqual(replace_weather("Northwest"), "NW")
        self.assertEqual(replace_weather("Northeast"), "NE")
        self.assertEqual(replace_weather("Southwest"), "SW")
        self.assertEqual(replace_weather("Southeast"), "SE")
        self.assertEqual(replace_weather("North"), "N")
        self.assertEqual(replace_weather("South"), "S")
        self.assertEqual(replace_weather("East"), "E")
        self.assertEqual(replace_weather("West"), "W")
        
        # Test replacing weather terms
        self.assertEqual(replace_weather("precipitation"), "precip")
        self.assertEqual(replace_weather("showers"), "shwrs")
        self.assertEqual(replace_weather("thunderstorms"), "t-storms")


if __name__ == '__main__':
    unittest.main()