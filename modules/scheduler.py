# modules/scheduler.py 2025 meshing-around
# Scheduler setup for Mesh Bot
import asyncio
import schedule
from datetime import datetime
from functools import partial
from modules.log import logger
from modules.settings import MOTD
from modules.system import send_message

async def run_scheduler_loop(interval=1):
    logger.debug(f"System: Scheduler loop started Tasks: {len(schedule.jobs)}, Details:{extract_schedule_fields(schedule.get_jobs())}")
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
            do_idx = part.find('do ')
            if do_idx != -1:
                summary = part[start:do_idx].strip()
                # Find the (last run: ... next run: ...) part
                paren_idx = part.find('(', do_idx)
                if paren_idx != -1:
                    summary += ' ' + part[paren_idx:].strip()
                    while '<function ' in summary:
                        f_start = summary.find('<function ')
                        f_end = summary.find('>', f_start)
                        if f_end == -1:
                            break
                        func_str = summary[f_start+10:f_end]
                        func_name = func_str.split(' ')[0]
                        summary = summary[:f_start] + func_name + summary[f_end+1:]
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
        scheduler_message = MOTD if schedulerMotd else schedulerMessage

        def send_sched_msg():
            send_message(scheduler_message, schedulerChannel, 0, schedulerInterface)

        # Basic Scheduler Options
        basicOptions = ['day', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'hour', 'min']
        if any(option in schedulerValue for option in basicOptions):
            if schedulerValue == 'day':
                if schedulerTime:
                    schedule.every().day.at(schedulerTime).do(send_sched_msg)
                else:
                    schedule.every(schedulerIntervalInt).days.do(send_sched_msg)
            elif 'mon' in schedulerValue and schedulerTime:
                schedule.every().monday.at(schedulerTime).do(send_sched_msg)
            elif 'tue' in schedulerValue and schedulerTime:
                schedule.every().tuesday.at(schedulerTime).do(send_sched_msg)
            elif 'wed' in schedulerValue and schedulerTime:
                schedule.every().wednesday.at(schedulerTime).do(send_sched_msg)
            elif 'thu' in schedulerValue and schedulerTime:
                schedule.every().thursday.at(schedulerTime).do(send_sched_msg)
            elif 'fri' in schedulerValue and schedulerTime:
                schedule.every().friday.at(schedulerTime).do(send_sched_msg)
            elif 'sat' in schedulerValue and schedulerTime:
                schedule.every().saturday.at(schedulerTime).do(send_sched_msg)
            elif 'sun' in schedulerValue and schedulerTime:
                schedule.every().sunday.at(schedulerTime).do(send_sched_msg)
            elif 'hour' in schedulerValue:
                schedule.every(schedulerIntervalInt).hours.do(send_sched_msg)
            elif 'min' in schedulerValue:
                schedule.every(schedulerIntervalInt).minutes.do(send_sched_msg)
            logger.debug(f"System: Starting the basic scheduler to send '{scheduler_message}' on schedule '{schedulerValue}' every {schedulerIntervalInt} interval at time '{schedulerTime}' on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'joke' in schedulerValue:
            schedule.every(schedulerIntervalInt).minutes.do(
                partial(send_message, tell_joke(), schedulerChannel, 0, schedulerInterface)
            )
            logger.debug(f"System: Starting the joke scheduler to send a joke every {schedulerIntervalInt} minutes on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'link' in schedulerValue:
            schedule.every(schedulerIntervalInt).hours.do(
                partial(send_message, handle_satpass(schedulerInterface, 'link'), schedulerChannel, 0, schedulerInterface)
            )
            logger.debug(f"System: Starting the link scheduler to send link messages every {schedulerIntervalInt} hours on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'weather' in schedulerValue:
            schedule.every().day.at(schedulerTime).do(
                partial(send_message, handle_wxc(0, schedulerInterface, 'wx', days=1), schedulerChannel, 0, schedulerInterface)
            )
            logger.debug(f"System: Starting the weather scheduler to send weather updates every {schedulerIntervalInt} hours on Device:{schedulerInterface} Channel:{schedulerChannel}")
        elif 'custom' in schedulerValue:
            try:
                from modules.custom_scheduler import setup_custom_schedules # type: ignore
                setup_custom_schedules(
                    send_message, tell_joke, welcome_message, handle_wxc, MOTD,
                    schedulerChannel, schedulerInterface)
                logger.debug(f"System: Starting the custom_scheduler.py ")
                schedule.every().monday.at("12:00").do(
                    lambda: logger.info("System: Scheduled Broadcast Enabled Reminder")
                )
            except Exception as e:
                logger.warning("Custom scheduler file not found or failed to import. cp etc/custom_scheduler.py modules/custom_scheduler.py")
    except Exception as e:
        logger.error(f"System: Scheduler Error {e}")
    return True