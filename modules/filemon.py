# File monitor module for the meshing-around bot
# 2024 Kelly Keeton K7MHI

from modules.log import *
import asyncio
import os

async def watch_file():
    def read_file(file_monitor_file_path):
        try:
            with open(file_monitor_file_path, 'r') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.warning(f"FileMon: Error reading file: {file_monitor_file_path}")
            return None
    
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