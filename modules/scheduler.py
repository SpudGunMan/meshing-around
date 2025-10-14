# modules/scheduler.py 2025 meshing-around
import schedule
from modules.log import logger
from modules.system import send_message, BroadcastScheduler

async def setup_scheduler(
    schedulerMotd, MOTD, schedulerMessage, schedulerChannel, schedulerInterface,
    schedulerValue, schedulerTime, schedulerInterval, logger, BroadcastScheduler
):
    # Setup the scheduler based on configuration
    try:
        if schedulerMotd:
            scheduler_message = MOTD
        else:
            scheduler_message = schedulerMessage

        if schedulerValue != '':
            if schedulerValue.lower() == 'day':
                if schedulerTime != '':
                    schedule.every().day.at(schedulerTime).do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
                else:
                    schedule.every(int(schedulerInterval)).days.do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            elif 'mon' in schedulerValue.lower() and schedulerTime != '':
                schedule.every().monday.at(schedulerTime).do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            elif 'tue' in schedulerValue.lower() and schedulerTime != '':
                schedule.every().tuesday.at(schedulerTime).do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            elif 'wed' in schedulerValue.lower() and schedulerTime != '':
                schedule.every().wednesday.at(schedulerTime).do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            elif 'thu' in schedulerValue.lower() and schedulerTime != '':
                schedule.every().thursday.at(schedulerTime).do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            elif 'fri' in schedulerValue.lower() and schedulerTime != '':
                schedule.every().friday.at(schedulerTime).do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            elif 'sat' in schedulerValue.lower() and schedulerTime != '':
                schedule.every().saturday.at(schedulerTime).do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            elif 'sun' in schedulerValue.lower() and schedulerTime != '':
                schedule.every().sunday.at(schedulerTime).do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            elif 'hour' in schedulerValue.lower():
                schedule.every(int(schedulerInterval)).hours.do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            elif 'min' in schedulerValue.lower():
                schedule.every(int(schedulerInterval)).minutes.do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            logger.debug(f"System: Starting the scheduler to send '{scheduler_message}' on schedule '{schedulerValue}' every {schedulerInterval} interval at time '{schedulerTime}' on Device:{schedulerInterface} Channel:{schedulerChannel}")
        else:
            # Default schedule if no valid configuration is provided
            # custom scheduler job to run the schedule see examples below
            logger.debug(f"System: Starting the scheduler to send '{scheduler_message}' every Monday at noon on Device:{schedulerInterface} Channel:{schedulerChannel}")
            schedule.every().monday.at("12:00").do(lambda: logger.info("System: Scheduled Broadcast Enabled Reminder"))

        # Start the Broadcast Scheduler
        await BroadcastScheduler()
    except Exception as e:
        logger.error(f"System: Scheduler Error {e}")

# Enhanced Examples of using the scheduler, Times here are in 24hr format
# https://schedule.readthedocs.io/en/stable/

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

# Send a joke every 6 hours using tell_joke function to channel 2 on device 1
#schedule.every(6).hours.do(lambda: send_message(tell_joke(), 2, 0, 1))

# Send a joke every 2 minutes using tell_joke function to channel 2 on device 1
#schedule.every(2).minutes.do(lambda: send_message(tell_joke(), 2, 0, 1))

# Send the Welcome Message every other day at 08:00 using send_message function to channel 2 on device 1
#schedule.every(2).days.at("08:00").do(lambda: send_message(welcome_message, 2, 0, 1))

# Send the MOTD every day at 13:00 using send_message function to channel 2 on device 1
#schedule.every().day.at("13:00").do(lambda: send_message(MOTD, 2, 0, 1))

# Send bbslink looking for peers every other day at 10:00 using send_message function to channel 3 on device 1
#schedule.every(2).days.at("10:00").do(lambda: send_message("bbslink MeshBot looking for peers", 3, 0, 1))