import schedule
from modules.log import logger
from modules.system import send_message

def setup_custom_schedules(send_message, tell_joke, welcome_message, handle_wxc, MOTD, schedulerChannel, schedulerInterface):
    # custom scheduler job to run the schedule see examples below
    logger.debug(f"System: Starting the custom scheduler default to send reminder every Monday at noon on Device:{schedulerInterface} Channel:{schedulerChannel}")
    schedule.every().monday.at("12:00").do(lambda: logger.info("System: Scheduled Broadcast Enabled Reminder"))


    # Enhanced Examples of using the scheduler, Times here are in 24hr format
    # https://schedule.readthedocs.io/en/stable/

    # Send a joke every 2 minutes
    #schedule.every(2).minutes.do(lambda: send_message(tell_joke(), schedulerChannel, 0, schedulerInterface))

    # Good Morning Every day at 09:00 using send_message function to channel 2 on device 1
    #schedule.every().day.at("09:00").do(lambda: send_message("Good Morning", 2, 0, 1))

    # Send WX every Morning at 08:00 using handle_wxc function to channel 2 on device 1
    #schedule.every().day.at("08:00").do(lambda: send_message(handle_wxc(0, 1, 'wx'), 2, 0, 1))

    # Send Weather Channel Notice Wed. Noon on channel 2, device 1
    #schedule.every().wednesday.at("12:00").do(lambda: send_message("Weather alerts available on 'Alerts' channel with default 'AQ==' key.", 2, 0, 1))

    # Send config URL for Medium Fast Network Use every other day at 10:00 to default channel 2 on device 1
    #schedule.every(2).days.at("10:00").do(lambda: send_message("Join us on Medium Fast https://meshtastic.org/e/#CgcSAQE6AggNEg4IARAEOAFAA0gBUB5oAQ", 2, 0, 1))

    # Send a Net Starting Now Message Every Wednesday at 19:00 using send_message function to channel 2 on device 1
    #schedule.every().wednesday.at("19:00").do(lambda: send_message("Net Starting Now", 2, 0, 1))

    # Send a Welcome Notice for group on the 15th and 25th of the month at 12:00 using send_message function to channel 2 on device 1
    #schedule.every().day.at("12:00").do(lambda: send_message("Welcome to the group", 2, 0, 1)).day(15, 25)

    # Send a Welcome Notice for group on the 15th and 25th of the month at 12:00
    #schedule.every().day.at("12:00").do(lambda: send_message("Welcome to the group", schedulerChannel, 0, schedulerInterface)).day(15, 25)

    # Send a joke every 6 hours
    #schedule.every(6).hours.do(lambda: send_message(tell_joke(), schedulerChannel, 0, schedulerInterface))

    # Send the Welcome Message every other day at 08:00
    #schedule.every(2).days.at("08:00").do(lambda: send_message(welcome_message, schedulerChannel, 0, schedulerInterface))

    # Send the MOTD every day at 13:00
    #schedule.every().day.at("13:00").do(lambda: send_message(MOTD, schedulerChannel, 0, schedulerInterface))

    # Send bbslink looking for peers every other day at 10:00
    #schedule.every(2).days.at("10:00").do(lambda: send_message("bbslink MeshBot looking for peers", schedulerChannel, 0, schedulerInterface))