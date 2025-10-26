import schedule
from modules.log import logger
from modules.settings import MOTD
from modules.system import send_message

def setup_custom_schedules(send_message, tell_joke, welcome_message, handle_wxc, MOTD, schedulerChannel, schedulerInterface):
    """
    Set up all custom schedules. Edit this function to add or remove scheduled tasks.
    """

    ### Example schedules
    # Send a joke every 2 minutes
    #schedule.every(2).minutes.do(send_joke, send_message, tell_joke, schedulerChannel, schedulerInterface)
    # Send a good morning message every day at 9 AM
    #schedule.every().day.at("09:00").do(send_good_morning, send_message, schedulerChannel, schedulerInterface)
    # Send weather update every day at 8 AM
    #schedule.every().day.at("08:00").do(send_wx, send_message, handle_wxc, schedulerChannel, schedulerInterface)
    # Send weather alerts every Wednesday at noon
    #schedule.every().wednesday.at("12:00").do(send_weather_alert, send_message, schedulerChannel, schedulerInterface)
    # Send configuration URL every 2 days at 10 AM
    #schedule.every(2).days.at("10:00").do(send_config_url, send_message, schedulerChannel, schedulerInterface)
    # Send net starting message every Wednesday at 7 PM
    #schedule.every().wednesday.at("19:00").do(send_net_starting, send_message, schedulerChannel, schedulerInterface)
    # Send welcome message every 2 days at 8 AM
    #schedule.every(2).days.at("08:00").do(send_welcome, send_message, schedulerChannel, schedulerInterface)
    # Send MOTD every day at 1 PM
    #schedule.every().day.at("13:00").do(send_motd, send_message, MOTD, schedulerChannel, schedulerInterface)
    # Send bbslink message every 2 days at 10 AM
    #schedule.every(2).days.at("10:00").do(send_message("bbslink MeshBot looking for peers", schedulerChannel, 0, schedulerInterface))

# Example task functions, modify as needed the channel and interface parameters default to schedulerChannel and schedulerInterface

def send_joke(send_message, tell_joke, channel, interface):
    send_message(tell_joke(), channel, 0, interface)

def send_good_morning(send_message, channel, interface):
    send_message("Good Morning", channel, 0, interface)

def send_wx(send_message, handle_wxc, channel, interface):
    send_message(handle_wxc(0, 1, 'wx', days=1), channel, 0, interface)

def send_weather_alert(send_message, channel, interface):
    send_message("Weather alerts available on 'Alerts' channel with default 'AQ==' key.", channel, 0, interface)

def send_config_url(send_message, channel, interface):
    send_message("Join us on Medium Fast https://meshtastic.org/e/#CgcSAQE6AggNEg4IARAEOAFAA0gBUB5oAQ", channel, 0, interface)

def send_net_starting(send_message, channel, interface):
    send_message("Net Starting Now", channel, 0, interface)

def send_welcome(send_message, channel, interface):
    send_message("Welcome to the group", channel, 0, interface)

def send_motd(send_message, MOTD, channel, interface):
    send_message(MOTD, channel, 0, interface)

def send_bbslink(send_message, channel, interface):
    send_message("bbslink MeshBot looking for peers", channel, 0, interface)
