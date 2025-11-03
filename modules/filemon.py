# File monitor module for the meshing-around bot
# 2024 Kelly Keeton K7MHI

from modules.log import logger
from modules.settings import (
    file_monitor_file_path,
    news_file_path,
    news_random_line_only,
    news_block_mode,
    allowXcmd,
    bbs_admin_list,
    xCmd2factorEnabled,
    xCmd2factor_timeout,
    enable_runShellCmd
    )
import asyncio
import random
import os
import subprocess
from datetime import datetime, timedelta

trap_list_filemon = ("readnews",)

NEWS_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
newsSourcesList = []

def read_file(file_monitor_file_path, random_line_only=False, news_block_mode=False):
    logger.debug(f"FileMon: Reading file: {file_monitor_file_path} options - random_line_only: {random_line_only}, news_block_mode: {news_block_mode}")
    try:
        if not os.path.exists(file_monitor_file_path):
            if file_monitor_file_path == "bee.txt":
                return "🐝buzz 💐buzz buzz🍯"
        if news_block_mode:
            # read a random block (separated by 2+ blank lines, robust to line endings)
            with open(file_monitor_file_path, 'r', encoding='utf-8') as f:
                content = f.read().replace('\r\n', '\n').replace('\r', '\n')
                blocks = []
                block = []
                for line in content.split('\n'):
                    if line.strip() == '':
                        if block:
                            blocks.append('\n'.join(block).strip())
                            block = []
                    else:
                        block.append(line)
                if block:
                    blocks.append('\n'.join(block).strip())
                blocks = [b for b in blocks if b]
                return random.choice(blocks) if blocks else None
        elif random_line_only:
            # read a random line from the file
            with open(file_monitor_file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                return random.choice(lines) if lines else None
        else:
            # read the whole file
            with open(file_monitor_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
    except Exception as e:
        logger.warning(f"FileMon: Error reading file: {file_monitor_file_path}")
        return None

def read_news(source=None, random_line_only=False, news_block_mode=False):
    # Reads the news file. If a source is provided, reads {source}_news.txt.
    if source:
        file_path = os.path.join(NEWS_DATA_DIR, f"{source}_news.txt")
    else:
        file_path = os.path.join(NEWS_DATA_DIR, news_file_path)
    # Block mode takes precedence over line mode
    if news_block_mode:
        return read_file(file_path, random_line_only=False, news_block_mode=True)
    elif random_line_only:
        return read_file(file_path, random_line_only=True, news_block_mode=False)
    else:
        return read_file(file_path)

def write_news(content, append=False):
    # write the news file on demand
    try:
        file_path = os.path.join(NEWS_DATA_DIR, news_file_path)
        with open(file_path, 'a' if append else 'w', encoding='utf-8') as f:
            #f.write(content)
            logger.info(f"FileMon: Updated {file_path}")
        return True
    except Exception as e:
        logger.warning(f"FileMon: Error writing file: {file_path}")
        return False

async def watch_file():
    # Watch the file for changes and return the new content when it changes
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
    # If no path is given, assume script/ directory
    if "/" not in script and "\\" not in script:
        script = os.path.join("script", script)
    try:
        current_working_directory = os.getcwd()
        script_path = os.path.join(current_working_directory, script)

        if not os.path.exists(script_path):
            # Try the raw script name
            script_path = script
            if not os.path.exists(script_path):
                logger.warning(f"FileMon: Script not found: {script_path}")
                return "sorry I can't do that"

        result = subprocess.run(
            ["bash", script_path, message],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            logger.error(f"FileMon: Script error: {result.stderr.strip()}")
            return None

        output = result.stdout.strip()
        return output if output else None
    except Exception as e:
        logger.warning(f"FileMon: Error calling external script: {e}")
        return None


waitingXroom = {}   # {message_from_id: (expected_answer, original_command, timestamp)}
def handleShellCmd(message, message_from_id, channel_number, isDM, deviceID):
    if not allowXcmd:
        return "x: command is disabled"
    if str(message_from_id) not in bbs_admin_list:
        logger.warning(f"FileMon: Unauthorized x: command attempt from {message_from_id}")
        return "x: command not authorized"
    if not isDM:
        return "x: command not authorized in group chat"

    # 2FA logic
    if xCmd2factorEnabled:
        timeNOW = datetime.utcnow()
        # If user is waiting for 2FA, treat message as answer
        if message_from_id in waitingXroom:
            answer = message[2:].strip() if message.lower().startswith("x:") else message.strip()
            expected, orig_command, ts = waitingXroom[message_from_id]
            if timeNOW - ts > timedelta(seconds=xCmd2factor_timeout):
                del waitingXroom[message_from_id]
                return "x2FA timed out, please try again"
            if answer == str(expected):
                del waitingXroom[message_from_id]
                # Run the original command
                try:
                    logger.info(f"FileMon: Running shell command from {message_from_id}: {orig_command}")
                    result = subprocess.run(orig_command, shell=True, capture_output=True, text=True, timeout=10, start_new_session=True)
                    output = result.stdout.strip()
                    return output if output else "✅ x: processed finished, no output"
                except Exception as e:
                    logger.warning(f"FileMon: Error running shell command: {e}")
                    logger.debug(f"FileMon: This command is not good for use over the mesh network")
                    return "x: error running command"
            else:
                logger.warning(f"FileMon: 🚨Incorrect 2FA answer from {message_from_id}")
                return "x2FA incorrect, try again"
        # If not waiting, treat as new command and issue challenge
        if message.lower().startswith("x:"):
            command = message[2:].strip()
            # Generate two random numbers, seed with message_from_id and time of day
            seed = timeNOW.second + timeNOW.minute * 60 + timeNOW.hour * 3600 + int(message_from_id)
            rnd = random.Random(seed)
            a = rnd.randint(10, 99)
            b = rnd.randint(10, 99)
            expected = a + b
            waitingXroom[message_from_id] = (expected, command, timeNOW)
            return f"x2FA required.\nReply `x: answer`\nWhat is {a} + {b}? "
        else:
            return "invalid command format"

    # If we reach here, 2FA is disabled or passed
    if enable_runShellCmd:
        if message.lower().startswith("x:"):
            command = message[2:].strip()
        else:
            return "invalid command format"
        try:
            logger.info(f"FileMon: Running shell command from {message_from_id}: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10, start_new_session=True)
            output = result.stdout.strip()
            return output if output else "x: command executed with no output"
        except Exception as e:
            logger.warning(f"FileMon: Error running shell command: {e}")
            logger.debug(f"FileMon: This command is not good for use over the mesh network")
            return "error running command"
    else:
        logger.debug("FileMon: x: command is disabled by no enable_runShellCmd")
        return "command is disabled"

def initNewsSources():
    #check for the files _news.txt and add to the newsHeadlines list
    global newsSourcesList
    newsSourcesList = []
    for file in os.listdir(NEWS_DATA_DIR):
        if file.endswith('_news.txt'):
            source = file[:-9]  # remove _news.txt
            newsSourcesList.append(source)
            return True
    logger.info("FileMon: No news sources found")
    return False

#initialize the headlines on startup
initNewsSources()
