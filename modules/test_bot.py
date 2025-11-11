# test_bot.py
# Unit tests for various modules in the meshing-around project
import os
import sys

# Add the parent directory to sys.path to allow module imports
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_path)

import unittest
import importlib
import pkgutil
import warnings
from modules.log import logger
from modules.settings import latitudeValue, longitudeValue
# Suppress ResourceWarning warnings for asyncio unclosed event  here
warnings.filterwarnings("ignore", category=ResourceWarning)


modules_path = os.path.join(parent_path, 'modules')

# Limits API calls during testing
CHECKALL = False
# Check for a file named .checkall in the parent directory
checkall_path = os.path.join(parent_path, '.checkall')
if os.path.isfile(checkall_path):
    CHECKALL = True


# List of module names to exclude
exclude = ['test_bot','udp', 'system', 'log', 'gpio', 'web',]
available_modules = [
    m.name for m in pkgutil.iter_modules([modules_path])
    if m.name not in exclude]

try:
    print("\nImporting Core Modules:")
    from modules.log import logger, getPrettyTime
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

    def test_load_bbsdb(self):
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

    def test_initialize_inventory_database(self):
        from inventory import initialize_inventory_database, process_inventory_command
        result = initialize_inventory_database()
        result1 = process_inventory_command(0, 'inventory', name="none")
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

    def test_send_ollama_query(self):
        from llm import send_ollama_query
        response = send_ollama_query("Hello, Ollama!")
        self.assertIsInstance(response, str)

    def test_extract_search_terms(self):
        from llm import extract_search_terms
        # Test with capitalized terms
        terms = extract_search_terms("What is Python programming?")
        self.assertIsInstance(terms, list)
        self.assertTrue(len(terms) > 0)
        # Test with multiple capitalized words
        terms2 = extract_search_terms("Tell me about Albert Einstein and Marie Curie")
        self.assertIsInstance(terms2, list)
        self.assertTrue(len(terms2) > 0)

    def test_get_wiki_context(self):
        from llm import get_wiki_context
        # Test with a well-known topic
        context = get_wiki_context("Python programming language")
        self.assertIsInstance(context, str)
        # Context might be empty if wiki is disabled or fails, that's ok

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
        summary = get_kiwix_summary("Python")
        self.assertIsInstance(summary, str)

    def get_openskynetwork(self):
        from locationdata import get_openskynetwork
        flights = get_openskynetwork(lat, lon)
        self.assertIsInstance(flights, str)

    def test_initalize_qrz_database(self):
        from qrz import initalize_qrz_database
        result = initalize_qrz_database()
        self.assertTrue(result)

    def test_import_radio_module(self):
        try:
            import radio
        #frequency = get_hamlib('f')
        #self.assertIsInstance(frequency, str)
        except Exception as e:
            self.fail(f"Importing radio module failed: {e}")

    def test_get_rss_feed(self):
        from rss import get_rss_feed
        result = get_rss_feed('')
        self.assertIsInstance(result, str)

    
    ##### GAMES Tests #####
    def test_jokes(self):
        from modules.games.joke import tell_joke
        haha = tell_joke(nodeID=0, test=True)
        print("Joke response:", haha)
        self.assertIsInstance(haha, str)
    
    def test_tictactoe_initial_and_move(self):
        from games.tictactoe import TicTacToe
        # Create an instance (no display module required for tests)
        tictactoe = TicTacToe(display_module=None)
        user_id = "testuser"
        # Start a new game (no move yet)
        initial = tictactoe.play(user_id, "")
        print("Initial response:", initial)
        # Make a move, e.g., '1'
        second = tictactoe.play(user_id, "1")
        print("After move '1':", second)
        self.assertIsInstance(initial, str)
        self.assertIsInstance(second, str)
    
    def test_playVideoPoker(self):
        from games.videopoker import playVideoPoker
        user_id = "testuser"
        # Start a new game/session
        initial = playVideoPoker(user_id, 'deal')
        print("Initial response:", initial)
        # Place a 5-coin bet
        after_bet = playVideoPoker(user_id, '5')
        print("After placing 5-coin bet:", after_bet)
        self.assertIsInstance(initial, str)
        self.assertIsInstance(after_bet, str)

    def test_play_blackjack(self):
        from games.blackjack import playBlackJack
        user_id = "testuser"
        # Start a new game/session
        initial = playBlackJack(user_id, 'deal')
        print("Initial response:", initial)
        # Place a 5-chip bet
        after_bet = playBlackJack(user_id, '5')
        print("After placing 5-chip bet:", after_bet)
        self.assertIsInstance(initial, str)
        self.assertIsInstance(after_bet, str)


    def test_hangman_initial_and_guess(self):
        from games.hangman import hangman
        user_id = "testuser"
        # Start a new game (no guess yet)
        initial = hangman.play(user_id, "")
        print("Initial response:", initial)
        # Guess a letter, e.g., 'e'
        second = hangman.play(user_id, "e")
        print("After guessing 'e':", second)
        self.assertIsInstance(initial, str)
        self.assertIsInstance(second, str)

   
    def test_play_lemonade_stand(self):
        from games.lemonade import playLemonstand, lemonadeTracker
        user_id = "testuser"
        # Ensure user is in tracker
        if not any(u['nodeID'] == user_id for u in lemonadeTracker):
            lemonadeTracker.append({'nodeID': user_id, 'cups': 0, 'lemons': 0, 'sugar': 0, 'cash': 30.0, 'start': 30.0, 'cmd': 'new', 'last_played': 0})
        # Start a new game
        initial = playLemonstand(user_id, "", newgame=True)
        print("Initial response:", initial)
        # Buy 1 box of cups
        after_cups = playLemonstand(user_id, "1")
        print("After buying 1 box of cups:", after_cups)
        self.assertIsInstance(initial, str)
        self.assertIsInstance(after_cups, str)

    
    def test_play_golfsim_one_hole(self):
        from games.golfsim import playGolf
        user_id = "testuser"
        # Start a new game/hole
        initial = playGolf(user_id, "", last_cmd="new")
        print("Initial hole info:", initial)
        # Take first shot with driver
        after_shot = playGolf(user_id, "driver")
        print("After hitting driver:", after_shot)
        self.assertIsInstance(initial, str)
        self.assertIsInstance(after_shot, str)

    
    def test_play_dopewar_choose_city_and_list(self):
        from games.dopewar import playDopeWars
        user_id = 1234567899  # Use a unique test user ID
        # Start a new game, get city selection prompt
        initial = playDopeWars(user_id, "")
        print("Initial city selection:", initial)
        # Choose city 1
        after_city = playDopeWars(user_id, "1")
        print("After choosing city 1 (main game list):", after_city)
        self.assertIsInstance(initial, str)
        self.assertIsInstance(after_city, str)

    
    def test_play_mastermind_one_guess(self):
        from games.mmind import start_mMind
        user_id = 1234567899  # Use a unique test user ID
        # Start a new game (should prompt for difficulty/colors)
        initial = start_mMind(user_id, "n")
        print("Initial response (difficulty/colors):", initial)
        # Make a guess (e.g., "RGBY" - valid for normal)
        after_guess = start_mMind(user_id, "RGBY")
        print("After guessing RGBY:", after_guess)
        self.assertIsInstance(initial, str)
        self.assertIsInstance(after_guess, str)


    def test_quiz_game_answer_one_and_end(self):
        from games.quiz import quizGamePlayer
        quizmaster_id = "admin"  # Use a valid quizmaster ID from bbs_admin_list
        user_id = "testuser"
        # Start the quiz as quizmaster
        start_msg = quizGamePlayer.start_game(quizmaster_id)
        print("Quiz start:", start_msg)
        # User joins the quiz
        join_msg = quizGamePlayer.join(user_id)
        print("User joined:", join_msg)
        # Get the first question (should be included in join_msg, but call explicitly for clarity)
        question_msg = quizGamePlayer.next_question(user_id)
        print("First question:", question_msg)
        # Simulate answering with 'A' (adjust if your first question expects a different answer)
        answer_msg = quizGamePlayer.answer(user_id, "A")
        print("Answer response:", answer_msg)
        # End the quiz as quizmaster
        end_msg = quizGamePlayer.stop_game(quizmaster_id)
        print("Quiz end:", end_msg)
        self.assertIsInstance(start_msg, str)
        self.assertIsInstance(join_msg, str)
        self.assertIsInstance(question_msg, str)
        self.assertIsInstance(answer_msg, str)
        self.assertIsInstance(end_msg, str)

    def test_survey_answer_one_and_end(self):
        from survey import survey_module
        user_id = "testuser"
        survey_name = "example"  # Make sure this survey exists in your data/surveys directory

        # Start the survey
        start_msg = survey_module.start_survey(user_id, survey_name)
        print("Survey start:", start_msg)
        # Answer the first question with 'A' (adjust if your survey expects a different type)
        answer_msg = survey_module.answer(user_id, "A")
        print("Answer response:", answer_msg)
        # End the survey
        end_msg = survey_module.end_survey(user_id)
        print("Survey end:", end_msg)

        self.assertIsInstance(start_msg, str)
        self.assertIsInstance(answer_msg, str)
        self.assertIsInstance(end_msg, str)


    def test_hamtest_answer_one(self):
        from games.hamtest import hamtest
        user_id = "testuser"
        # Start a new ham test game (default level: technician)
        initial = hamtest.newGame(user_id)
        print("Initial question:", initial)
        # Answer the first question with 'A'
        answer_msg = hamtest.answer(user_id, "A")
        print("Answer response:", answer_msg)
        self.assertIsInstance(initial, str)
        self.assertIsInstance(answer_msg, str)


    ##### API Tests - Extended tests run only if CHECKALL is True #####


    if CHECKALL:
        logger.info("Running extended API tests as CHECKALL is enabled.")
    def test_handledxcluster(self):
        from modules.dxspot import handledxcluster
        test_message = "DX band=20m mode=SSB of=K7MHI"
        response = handledxcluster(test_message, nodeID=0, deviceID='testdevice')
        print("DX Spotter response:", response)
        self.assertIsInstance(response, str)

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

        def test_where_am_i(self):
            from locationdata import where_am_i
            location = where_am_i(lat, lon)
            self.assertIsInstance(location, str)

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

        def test_getNextSatellitePass(self):
            from space import getNextSatellitePass
            pass_info = getNextSatellitePass('25544', lat, lon)
            self.assertIsInstance(pass_info, str)  

        def test_get_wx_meteo(self):
            from wx_meteo import get_wx_meteo
            weather_report = get_wx_meteo(lat, lon)
            self.assertIsInstance(weather_report, str)

        def test_get_flood_openmeteo(self):
            from wx_meteo import get_flood_openmeteo
            flood_report = get_flood_openmeteo(lat, lon)
            self.assertIsInstance(flood_report, str)

    def test_check_callsign_match(self):
        # Test the callsign filtering function for WSJT-X/JS8Call
        from radio import check_callsign_match
        
        # Test with empty filter (should match all)
        self.assertTrue(check_callsign_match("CQ K7MHI CN87", []))
        
        # Test exact match
        self.assertTrue(check_callsign_match("CQ K7MHI CN87", ["K7MHI"]))
        
        # Test case insensitive match
        self.assertTrue(check_callsign_match("CQ k7mhi CN87", ["K7MHI"]))
        self.assertTrue(check_callsign_match("CQ K7MHI CN87", ["k7mhi"]))
        
        # Test no match
        self.assertFalse(check_callsign_match("CQ W1AW FN31", ["K7MHI"]))
        
        # Test multiple callsigns
        self.assertTrue(check_callsign_match("CQ W1AW FN31", ["K7MHI", "W1AW"]))
        self.assertTrue(check_callsign_match("K7MHI DE W1AW", ["K7MHI", "W1AW"]))
        
        # Test portable/mobile suffixes
        self.assertTrue(check_callsign_match("CQ K7MHI/P CN87", ["K7MHI"]))
        self.assertTrue(check_callsign_match("W1AW-7", ["W1AW"]))
        
        # Test no false positives with partial matches
        self.assertFalse(check_callsign_match("CQ K7MHIX CN87", ["K7MHI"]))
        self.assertFalse(check_callsign_match("K7 TEST", ["K7MHI"]))




if __name__ == '__main__':
    if not CHECKALL:
        print("\nNote: Extended API tests are skipped. To enable them, create a file named '.checkall' in the parent directory.\n")
    unittest.main()