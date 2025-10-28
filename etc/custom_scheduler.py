import schedule
from modules.log import logger
from modules.settings import MOTD
from modules.system import send_message

def setup_custom_schedules(send_message, tell_joke, welcome_message, handle_wxc, MOTD, schedulerChannel, schedulerInterface):
    """
    Set up custom schedules. Edit the example schedules as needed.
    
    1. in config.ini set "value" under [scheduler] to:  value = custom    
    2. edit this file to add/remove/modify schedules
    3. restart mesh bot
    4. verify schedules are working by checking the log file
    5. Make sure to uncomment (delete the single #) the example schedules down at the end of the file to enable them
    Python is sensitive to indentation so be careful when editing this file. 
    https://thonny.org is included on pi's image and is a simple IDE to use for editing python files.
    """
    try:
        # Example task functions, modify as needed the channel and interface parameters default to schedulerChannel and schedulerInterface
        def send_joke(channel, interface):
            ## uses system.send_message to send the result of tell_joke()
            send_message(tell_joke(), channel, 0, interface)

        def send_good_morning(channel, interface):
            ## uses system.send_message to send "Good Morning"
            send_message("Good Morning", channel, 0, interface)

        def send_wx(channel, interface):
            ## uses system.send_message to send the result of handle_wxc(id,id,cmd,days_returned)
            send_message(handle_wxc(0, 1, 'wx', days=1), channel, 0, interface)

        def send_weather_alert(channel, interface):
            ## uses system.send_message to send string
            send_message("Weather alerts available on 'Alerts' channel with default 'AQ==' key.", channel, 0, interface)

        def send_config_url(channel, interface):
            ## uses system.send_message to send string
            send_message("Join us on Medium Fast https://meshtastic.org/e/#CgcSAQE6AggNEg4IARAEOAFAA0gBUB5oAQ", channel, 0, interface)

        def send_net_starting(channel, interface):
            ## uses system.send_message to send string, channel 2, interface 3
            send_message("Net Starting Now", 2, 0, 3)

        def send_welcome(channel, interface):
            ## uses system.send_message to send string, channel 2, interface 1
            send_message("Welcome to the group", 2, 0, 1)

        def send_motd(channel, interface):
            ## uses system.send_message to send message of the day string which can be updated in runtime
            send_message(MOTD, channel, 0, interface)

        ### Send a joke every 2 minutes
        #schedule.every(2).minutes.do(lambda: send_joke(schedulerChannel, schedulerInterface))
        ### Send a good morning message every day at 9 AM
        #schedule.every().day.at("09:00").do(lambda: send_good_morning(schedulerChannel, schedulerInterface))
        ### Send weather update every day at 8 AM
        #schedule.every().day.at("08:00").do(lambda: send_wx(schedulerChannel, schedulerInterface))
        ### Send weather alerts every Wednesday at noon
        #schedule.every().wednesday.at("12:00").do(lambda: send_weather_alert(schedulerChannel, schedulerInterface))
        ### Send configuration URL every 2 days at 10 AM
        #schedule.every(2).days.at("10:00").do(lambda: send_config_url(schedulerChannel, schedulerInterface))
        ### Send net starting message every Wednesday at 7 PM
        #schedule.every().wednesday.at("19:00").do(lambda: send_net_starting(schedulerChannel, schedulerInterface))
        ### Send welcome message every 2 days at 8 AM
        #schedule.every(2).days.at("08:00").do(lambda: send_welcome(schedulerChannel, schedulerInterface))
        ### Send MOTD every day at 1 PM
        #schedule.every().day.at("13:00").do(lambda: send_motd(schedulerChannel, schedulerInterface))
        ### Send bbslink message every 2 days at 10 AM
        #schedule.every(2).days.at("10:00").do(lambda: send_message("bbslink MeshBot looking for peers", schedulerChannel, 0, schedulerInterface))

    except Exception as e:
        logger.error(f"Error setting up custom schedules: {e}")