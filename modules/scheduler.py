# modules/scheduler.py 2025 meshing-around
# Scheduler setup for Mesh Bot
import asyncio
import schedule
from datetime import datetime
from modules.log import logger
from modules.settings import MOTD
from modules.system import send_message

async def run_scheduler_loop(interval=1):
    logger.debug("System: Scheduler loop started")
    try:
        last_logged_minute = -1
        while True:
            try:
                # Log scheduled jobs every 20 minutes
                now = datetime.now()
                if now.minute % 20 == 0 and now.minute != last_logged_minute:
                    logger.debug(f"System: Scheduled Tasks {len(schedule.jobs)}, Details:{extract_schedule_fields(schedule.get_jobs())}")
                    last_logged_minute = now.minute
                schedule.run_pending()
            except Exception as e:
                logger.error(f"System: Scheduler loop exception: {e}")
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        logger.debug("System: Scheduler loop cancelled, shutting down.")

def safe_int(val, default=0, type=""):
    try:
        return int(val)
    except (ValueError, TypeError):
        logger.debug(f"System: Scheduler config {type} error '{val}' to int, using default {default}")
        return default

def extract_schedule_fields(jobs):
    """
    Extracts 'Every ... (last run: [...], next run: ...)' from schedule.get_jobs() output without regex.
    """
    jobs_str = str(jobs)
    results = []
    # Split by '), ' to separate jobs, then add ')' back except last
    parts = jobs_str.split('), ')
    for i, part in enumerate(parts):
        if not part.endswith(')'):
            part += ')'
        # Find the start of 'Every'
        start = part.find('Every')
        if start != -1:
            # Find the start of 'do <lambda>()'
            do_idx = part.find('do <lambda>()')
            if do_idx != -1:
                summary = part[start:do_idx].strip()
                # Find the (last run: ... next run: ...) part
                paren_idx = part.find('(', do_idx)
                if paren_idx != -1:
                    summary += ' ' + part[paren_idx:].strip()
                    results.append(summary)
    return results

def setup_scheduler(
    schedulerMotd, MOTD, schedulerMessage, schedulerChannel, schedulerInterface,
    schedulerValue, schedulerTime, schedulerInterval):
    try:
        # Methods imported from mesh_bot for scheduling tasks
        from mesh_bot import (
            tell_joke,
            welcome_message,
            handle_wxc,
            handle_moon,
            handle_sun,
            handle_riverFlow,
            handle_tide,
            handle_satpass,
        )
    except ImportError as e:
        logger.warning(f"Some mesh_bot schedule features are unavailable by option disable in config.ini: {e} comment out the use of these methods in your custom_scheduler.py")
    
    # Setup the scheduler based on configuration
    schedulerValue = schedulerValue.lower().strip()
    schedulerTime = schedulerTime.strip()
    schedulerInterval = schedulerInterval.strip()
    schedulerChannel = safe_int(schedulerChannel, 0, type="channel")
    schedulerInterface = safe_int(schedulerInterface, 1, type="interface")
    schedulerIntervalInt = safe_int(schedulerInterval, 5, type="interval")

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
                    schedule.every(schedulerIntervalInt).days.do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
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
                schedule.every(schedulerIntervalInt).hours.do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            elif 'min' in schedulerValue.lower():
                schedule.every(schedulerIntervalInt).minutes.do(lambda: send_message(scheduler_message, schedulerChannel, 0, schedulerInterface))
            logger.debug(f"System: Starting the basic scheduler to send '{scheduler_message}' on schedule '{schedulerValue}' every {schedulerIntervalInt} interval at time '{schedulerTime}' on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'joke' in schedulerValue.lower():
            # Schedule to send a joke every specified interval
            schedule.every(schedulerIntervalInt).minutes.do(lambda: send_message(tell_joke(), schedulerChannel, 0, schedulerInterface))
            logger.debug(f"System: Starting the joke scheduler to send a joke every {schedulerIntervalInt} minutes on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'link' in schedulerValue.lower():
            # Schedule to send a link message every specified interval
            schedule.every(schedulerIntervalInt).hours.do(lambda: send_message(handle_satpass(schedulerInterface, 'link'), schedulerChannel, 0, schedulerInterface))
            logger.debug(f"System: Starting the link scheduler to send link messages every {schedulerIntervalInt} hours on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'weather' in schedulerValue.lower():
            # Schedule to send weather updates every specified interval
            schedule.every(schedulerIntervalInt).hours.do(lambda: send_message(handle_wxc(0, schedulerInterface, 'wx'), schedulerChannel, 0, schedulerInterface))
            logger.debug(f"System: Starting the weather scheduler to send weather updates every {schedulerIntervalInt} hours on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'custom' in schedulerValue.lower():
           # Import and setup custom schedules from custom_scheduler.py
            try:
                # This file is located in etc/custom_scheduler.py and copied to modules/custom_scheduler.py at install
                from modules.custom_scheduler import setup_custom_schedules # type: ignore  # pylance
                setup_custom_schedules(
                    send_message, tell_joke, welcome_message, handle_wxc, MOTD,
                    schedulerChannel, schedulerInterface)
                logger.debug("System: Custom scheduler file imported and custom schedules set up.")
            except Exception as e:
                logger.debug(f"System: Failed to import custom scheduler. {e}")
                logger.warning("Custom scheduler file not found or failed to import. cp etc/custom_scheduler.py modules/custom_scheduler.py")
    except Exception as e:
        logger.error(f"System: Scheduler Error {e}")
