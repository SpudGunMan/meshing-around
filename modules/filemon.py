# File monitor module for the meshing-around bot
# 2024 Kelly Keeton K7MHI

from modules.log import *
import asyncio
import random
import os
from pathlib import Path
from datetime import datetime

trap_list_filemon = ("readnews",)

def read_file(file_monitor_file_path, random_line_only=False):

    try:
        if not os.path.exists(file_monitor_file_path):
            logger.warning(f"FileMon: File not found: {file_monitor_file_path}")
            if file_monitor_file_path == "bee.txt":
                return "🐝buzz 💐buzz buzz🍯"
        if random_line_only:
            # read a random line from the file
            with open(file_monitor_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return random.choice(lines)
        else:
            # read the whole file
            with open(file_monitor_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
    except Exception as e:
        logger.warning(f"FileMon: Error reading file: {file_monitor_file_path}")
        return None
    
def read_news():
    # read the news file on demand
    return read_file(news_file_path, news_random_line_only)


def write_news(content, append=False):
    # write the news file on demand
    try:
        with open(news_file_path, 'a' if append else 'w', encoding='utf-8') as f:
            f.write(content)
            logger.info(f"FileMon: Updated {news_file_path}")
        return True
    except Exception as e:
        logger.warning(f"FileMon: Error writing file: {news_file_path}")
        return False

async def watch_file():
    
    if not os.path.exists(file_monitor_file_path):
        logger.warning(f"FileMon: Not exist: {file_monitor_file_path}")
        return None
    else:
        # Initialize the last_modified_time
        last_modified_time = os.path.getmtime(file_monitor_file_path)
        path_is_dir = os.path.isdir(file_monitor_file_path)
        if path_is_dir:
            last_modified_time = None   # Force processing of files in dir
        while True:
            await asyncio.sleep(60)  # Check every minute, to slow messaging
            if last_modified_time is None or ( (last_modified_time+60) < datetime.now() ):
                oldest_file_pathname = file_monitor_file_path
                if_delete_file = False # By default, do not delete file
                # logger.debug(f"FileMon: Watching: {oldest_file_pathname}")
                if path_is_dir:
                    # If it is a directory
                    # Get all files and sort by modification time (oldest first)
                    files_sorted_by_time = sorted(
                        [f for f in Path(file_monitor_file_path).iterdir() if f.is_file()],
                        key=os.path.getmtime
                    )

                    # Get the pathname of the first (oldest) file
                    if files_sorted_by_time:
                        oldest_file_pathname = files_sorted_by_time[0]
                        logger.debug(f"FileMon: Found file: {oldest_file_pathname}")
                        if_delete_file = True  # Delete this file when done

                current_modified_time = os.path.getmtime(oldest_file_pathname)
                if ( current_modified_time != last_modified_time ) or if_delete_file == True:
                    if oldest_file_pathname != file_monitor_file_path:
                        # File has been modified
                        logger.debug(f"FileMon: Reading file: {oldest_file_pathname}")
                        content = read_file(oldest_file_pathname)
                        last_modified_time = current_modified_time
                        # Cleanup the content
                        content = content.replace('\n', ' ').replace('\r', '').strip()
                        if if_delete_file == True:
                            if oldest_file_pathname != file_monitor_file_path:
                                try:
                                    logger.debug(f"FileMon: Deleting file: {oldest_file_pathname}")
                                    os.remove(oldest_file_pathname)
                                except Exception as e:
                                    logger.warning(f"FileMon: Error deleting file: {oldest_file_pathname}")
                                    # return False
                            if_delete_file = False
                        if content:
                            return content
                    else:
                        if_delete_file = False

def call_external_script(message, script="script/runShell.sh"):
    try:
        # Debugging: Print the current working directory and resolved script path
        current_working_directory = os.getcwd()
        script_path = os.path.join(current_working_directory, script)

        if not os.path.exists(script_path):
            # try the raw script name
            script_path = script
            if not os.path.exists(script_path):
                logger.warning(f"FileMon: Script not found: {script_path}")
                return "sorry I can't do that"
            
        output = os.popen(f"bash {script_path} {message}").read().encode('utf-8').decode('utf-8')
        return output
    except Exception as e:
        logger.warning(f"FileMon: Error calling external script: {e}")
        return None

def handleShellCmd(message, message_from_id, channel_number, isDM, deviceID):
    if not allowXcmd:
        return "x: command is disabled"

    if str(message_from_id) not in bbs_admin_list:
        logger.warning(f"FileMon: Unauthorized x: command attempt from {message_from_id}")
        return "x: command not authorized"

    if not isDM:
        return "x: command not authorized in group chat"

    if enable_runShellCmd:
        if message.lower().startswith("x:"):
            # Remove 'x:' (case-insensitive)
            command = message[2:]
            # If there's a space after 'x:', remove it
            if command.startswith(" "):
                command = command[1:]
            command = command.strip()
        else:
            return "x: invalid command format"

        try:
            logger.info(f"FileMon: Running shell command from {message_from_id}: {command}")
            output = os.popen(command).read().encode('utf-8').decode('utf-8')
            if output:
                return output
            else:
                return "x: command returned no output"
        except Exception as e:
            logger.warning(f"FileMon: Error running shell command: {e}")
            return "x: command error"
    else:
        logger.debug("FileMon: x: command is disabled by no enable_runShellCmd")
        return "x: command is disabled"
