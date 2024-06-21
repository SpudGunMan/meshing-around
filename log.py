from datetime import datetime

def log_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")