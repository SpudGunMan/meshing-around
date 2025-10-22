# modules/scheduler.py 2025 meshing-around
# Scheduler setup for Mesh Bot
import asyncio
import schedule
from modules.log import logger
from modules.system import send_message

async def setup_scheduler(
    schedulerMotd, MOTD, schedulerMessage, schedulerChannel, schedulerInterface,
    schedulerValue, schedulerTime, schedulerInterval, logger, BroadcastScheduler):
    
    # methods available for custom scheduler messages
    from mesh_bot import tell_joke, welcome_message, handle_wxc, handle_moon, handle_sun, handle_riverFlow, handle_tide, handle_satpass
    schedulerValue = schedulerValue.lower().strip()
    schedulerTime = schedulerTime.strip()
    schedulerInterval = schedulerInterval.strip()
    schedulerChannel = int(schedulerChannel)
    schedulerInterface = int(schedulerInterface)
    # Setup the scheduler based on configuration
    try:
        if schedulerMotd:
            scheduler_message = MOTD
        else:
            scheduler_message = schedulerMessage

        # Basic Scheduler Options
        basicOptions = ['day', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'hour', 'min']
        if any(option.lower() in schedulerValue.lower() for option in basicOptions):
            # Basic scheduler job to run the schedule see examples below for custom schedules
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
            logger.debug(f"System: Starting the basic scheduler to send '{scheduler_message}' on schedule '{schedulerValue}' every {schedulerInterval} interval at time '{schedulerTime}' on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'joke' in schedulerValue.lower():
            # Schedule to send a joke every specified interval
            schedule.every(int(schedulerInterval)).minutes.do(lambda: send_message(tell_joke(), schedulerChannel, 0, schedulerInterface))
            logger.debug(f"System: Starting the joke scheduler to send a joke every {schedulerInterval} minutes on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'weather' in schedulerValue.lower():
            # Schedule to send weather updates every specified interval
            schedule.every(int(schedulerInterval)).hours.do(lambda: send_message(handle_wxc(0, schedulerInterface, 'wx'), schedulerChannel, 0, schedulerInterface))
            logger.debug(f"System: Starting the weather scheduler to send weather updates every {schedulerInterval} hours on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'custom' in schedulerValue.lower():
           # Import and setup custom schedules from custom_scheduler.py
            try:
                from modules.custom_scheduler import setup_custom_schedules
                setup_custom_schedules(
                    send_message, tell_joke, welcome_message, handle_wxc, MOTD,
                    schedulerChannel, schedulerInterface)
                logger.debug("System: Custom scheduler file imported and custom schedules set up.")
            except ImportError:
                logger.warning("Custom scheduler file not found or failed to import. cp ecp etc/custom_scheduler.py modules/custom_scheduler.py")

        # Start the Broadcast Scheduler
        await BroadcastScheduler()
    except Exception as e:
        logger.error(f"System: Scheduler Error {e}")

