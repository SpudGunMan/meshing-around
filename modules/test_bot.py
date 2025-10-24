# test_bot.py
# Unit tests for various modules in the meshing-around project
import unittest
import os
import sys
import importlib
import pkgutil
# Add the parent directory to sys.path to allow module imports
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_path)
modules_path = os.path.join(parent_path, 'modules')

# List of module names to exclude
exclude = ['test_bot','udp', 'system', 'log', 'gpio', 'web',]
available_modules = [
    m.name for m in pkgutil.iter_modules([modules_path])
    if m.name not in exclude]

try:
    print("\nImporting Core Modules:")
    from modules.log import *
    print("  ✔ Imported 'log'")
    # Set location default
    lat = latitudeValue
    lon = longitudeValue
    print(f"  ✔ Location set to Latitude: {lat}, Longitude: {lon}")
    from modules.system import *
    print("  ✔ Imported 'system'")
    
    print("\nImporting non-excluded modules:")
    for module_name in [m.name for m in pkgutil.iter_modules([modules_path])]:
        if module_name not in exclude:
            importlib.import_module(module_name)
            print(f"  ✔ Imported '{module_name}'")
except Exception as e:
    print(f"\nError importing modules: {e}")
    print("Run this program from the main program directory: python3 script/test_bot.py")
    exit(1)

class TestBot(unittest.TestCase):
    def test_example(self):
        # Example test case
        self.assertEqual(1 + 1, 2)

    # bbstools.py
    def test_bbsdb_load(self):
        from bbstools import load_bbsdb
        test_load = load_bbsdb()
        self.assertTrue(test_load)
    
    def test_bbs_list_messages(self):
        from bbstools import bbs_list_messages
        messages = bbs_list_messages()
        print("list_messages() returned:", messages)
        self.assertIsInstance(messages, str)

    def test_initialize_checklist_database(self):
        from checklist import initialize_checklist_database, process_checklist_command
        result = initialize_checklist_database()
        result1 = process_checklist_command(0, 'checklist', name="none", location="none")
        self.assertTrue(result)
        self.assertIsInstance(result1, str)

    def test_init_news_sources(self):
        from filemon import initNewsSources
        result = initNewsSources()
        self.assertTrue(result)

    def test_get_nina_alerts(self):
        from globalalert import get_nina_alerts
        alerts = get_nina_alerts()
        self.assertIsInstance(alerts, str)

    def test_llmTool_get_google(self):
        from llm import llmTool_get_google
        result = llmTool_get_google("What is 2+2?",  1)
        self.assertIsInstance(result, list)

    def test_send_ollama_query(self):
        from llm import send_ollama_query
        response = send_ollama_query("Hello, Ollama!")
        self.assertIsInstance(response, str)

    def test_where_am_i(self):
        from locationdata import where_am_i
        location = where_am_i(lat, lon)
        self.assertIsInstance(location, str)

    def test_getRepeaterBook(self):
        from locationdata import getRepeaterBook
        repeaters = getRepeaterBook(lat, lon)
        self.assertIsInstance(repeaters, str)

    def test_getArtSciRepeaters(self):
        from locationdata import getArtSciRepeaters
        repeaters = getArtSciRepeaters(lat, lon)
        self.assertIsInstance(repeaters, str)

    def test_get_NOAAtides(self):
        from locationdata import get_NOAAtide
        tides = get_NOAAtide(lat, lon)
        self.assertIsInstance(tides, str)

    def test_get_NOAAweather(self):
        from locationdata import get_NOAAweather
        weather = get_NOAAweather(lat, lon)
        self.assertIsInstance(weather, str)

    def test_getWeatherAlertsNOAA(self):
        from locationdata import getWeatherAlertsNOAA
        alerts = getWeatherAlertsNOAA(lat, lon)
        if isinstance(alerts, tuple):
            self.assertIsInstance(alerts[0], str)
        else:
            self.assertIsInstance(alerts, str)
    
    def test_getActiveWeatherAlertsDetailNOAA(self):
        from locationdata import getActiveWeatherAlertsDetailNOAA
        alerts_detail = getActiveWeatherAlertsDetailNOAA(lat, lon)
        self.assertIsInstance(alerts_detail, str)
    
    def test_getIpawsAlerts(self):
        from locationdata import getIpawsAlert
        alerts = getIpawsAlert(lat, lon)
        self.assertIsInstance(alerts, str)
    
    def test_get_flood_noaa(self):
        from locationdata import get_flood_noaa
        flood_info = get_flood_noaa(lat, lon, 12484500)  # Example gauge UID
        self.assertIsInstance(flood_info, str)
    
    def test_get_volcano_usgs(self):
        from locationdata import get_volcano_usgs
        volcano_info = get_volcano_usgs(lat, lon)
        self.assertIsInstance(volcano_info, str)

    def test_get_nws_marine_alerts(self):
        from locationdata import get_nws_marine
        marine_alerts = get_nws_marine('https://tgftp.nws.noaa.gov/data/forecasts/marine/coastal/pz/pzz135.txt',1) # Example zone
        self.assertIsInstance(marine_alerts, str)

    def test_checkUSGSEarthQuakes(self):
        from locationdata import checkUSGSEarthQuake
        earthquakes = checkUSGSEarthQuake(lat, lon)
        self.assertIsInstance(earthquakes, str)

    def get_openskynetwork(self):
        from locationdata import get_openskynetwork
        flights = get_openskynetwork(lat, lon)
        self.assertIsInstance(flights, str)

    def test_initalize_qrz_database(self):
        from qrz import initalize_qrz_database
        result = initalize_qrz_database()
        self.assertTrue(result)

    def test_get_hamlib(self):
        from radio import get_hamlib
        frequency = get_hamlib('f')
        self.assertIsInstance(frequency, str)

    def test_get_rss_feed(self):
        from rss import get_rss_feed
        result = get_rss_feed('')
        self.assertIsInstance(result, str)

    def test_getNextSatellitePass(self):
        from space import getNextSatellitePass
        pass_info = getNextSatellitePass('25544', lat, lon)
        self.assertIsInstance(pass_info, str)

    def test_get_moon_phase(self):
        from space import get_moon
        phase = get_moon(lat, lon)
        self.assertIsInstance(phase, str)

    def test_get_sun_times(self):
        from space import get_sun
        sun_times = get_sun(lat, lon)
        self.assertIsInstance(sun_times, str)
    
    def test_hf_band_conditions(self):
        from space import hf_band_conditions
        conditions = hf_band_conditions()
        self.assertIsInstance(conditions, str)

    def test_get_wikipedia_summary(self):
        from wiki import get_wikipedia_summary
        summary = get_wikipedia_summary("Python", location=(lat, lon))
        self.assertIsInstance(summary, str)

    def test_get_kiwix_summary(self):
        from wiki import get_kiwix_summary
        summary = get_kiwix_summary("Python ")
        self.assertIsInstance(summary, str)
    
    




if __name__ == '__main__':    
    unittest.main()