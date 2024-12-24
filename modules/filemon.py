# File monitor module for the meshing-around bot
# 2024 Kelly Keeton K7MHI

from modules.log import *
import asyncio
import random
import os

trap_list_filemon = ("readnews",)

def read_file(file_monitor_file_path, random_line_only=False):

    try:
        if not os.path.exists(file_monitor_file_path):
            logger.warning(f"FileMon: File not found: {file_monitor_file_path}")
            if file_monitor_file_path == "bee.txt":
                return "🐝buzz 💐buzz buzz🍯"
        if random_line_only:
            # read a random line from the file
            with open(file_monitor_file_path, 'r') as f:
                lines = f.readlines()
                return random.choice(lines)
        else:
            # read the whole file
            with open(file_monitor_file_path, 'r') as f:
                content = f.read()
            return content
    except Exception as e:
        logger.warning(f"FileMon: Error reading file: {file_monitor_file_path}")
        return None
    
def read_news():
    # read the news file on demand
    return read_file(news_file_path, read_news_enabled)


def write_news(content, append=False):
    # write the news file on demand
    try:
        with open(news_file_path, 'a' if append else 'w') as f:
            f.write(content)
            logger.info(f"FileMon: Updated {news_file_path}")
        return True
    except Exception as e:
        logger.warning(f"FileMon: Error writing file: {news_file_path}")
        return False

async def watch_file():
    
    if not os.path.exists(file_monitor_file_path):
        return None
    else:
        last_modified_time = os.path.getmtime(file_monitor_file_path)
        while True:
            current_modified_time = os.path.getmtime(file_monitor_file_path)
            if current_modified_time != last_modified_time:
                # File has been modified
                content = read_file(file_monitor_file_path)
                last_modified_time = current_modified_time
                # Cleanup the content
                content = content.replace('\n', ' ').replace('\r', '').strip()
                if content:
                    return content
            await asyncio.sleep(1)  # Check every

def call_external_script(message, script="runShell.sh"):
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
            
        output = os.popen(f"bash {script_path} {message}").read()
        return output
    except Exception as e:
        logger.warning(f"FileMon: Error calling external script: {e}")
        return None
    