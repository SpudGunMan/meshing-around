import logging
from logging.handlers import TimedRotatingFileHandler
import re
from datetime import datetime
from modules.settings import *

class CustomFormatter(logging.Formatter):
    grey = '\x1b[38;21m'
    white = '\x1b[38;5;231m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    green = '\x1b[38;5;46m'
    purple = '\x1b[38;5;129m'
    bold_red = '\x1b[31;1m'
    bold_white = '\x1b[37;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.blue + self.fmt + self.reset,
            logging.INFO: self.white + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
class plainFormatter(logging.Formatter):
    ansi_escape = re.compile(r'\x1b\[([0-9]+)(;[0-9]+)*m')

    def format(self, record):
        message = super().format(record)
        return self.ansi_escape.sub('', message)

# Create logger
logger = logging.getLogger("MeshBot System Logger")
logger.setLevel(logging.DEBUG)
logger.propagate = False

msgLogger = logging.getLogger("MeshBot Messages Logger")
msgLogger.setLevel(logging.INFO)
msgLogger.propagate = False

# Define format for logs
logFormat = '%(asctime)s | %(levelname)8s | %(message)s'
msgLogFormat = '%(asctime)s | %(message)s'
today = datetime.now()

# Create stdout handler for logging to the console
stdout_handler = logging.StreamHandler()
# Set level for stdout handler (logs DEBUG level and above)
stdout_handler.setLevel(logging.DEBUG)
# Set format for stdout handler
stdout_handler.setFormatter(CustomFormatter(logFormat))
# Add handlers to the logger
logger.addHandler(stdout_handler)

if syslog_to_file:
    # Create file handler for logging to a file
    file_handler_sys = TimedRotatingFileHandler('logs/meshbot.log', when='midnight', backupCount=log_backup_count)
    file_handler_sys.setLevel(logging.DEBUG) # DEBUG used by default for system logs to disk
    file_handler_sys.setFormatter(plainFormatter(logFormat))
    logger.addHandler(file_handler_sys)

if log_messages_to_file:
    # Create file handler for logging to a file
    file_handler = TimedRotatingFileHandler('logs/messages.log', when='midnight', backupCount=log_backup_count)
    file_handler.setLevel(logging.INFO) # INFO used for messages to disk
    file_handler.setFormatter(logging.Formatter(msgLogFormat))
    msgLogger.addHandler(file_handler)