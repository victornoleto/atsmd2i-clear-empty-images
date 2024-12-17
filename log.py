import logging
import os
from logging.handlers import TimedRotatingFileHandler

log_path = 'logs'

Log = logging.getLogger(__name__)
Log.setLevel(logging.DEBUG)

# Ensure log directory exists
os.makedirs(log_path, exist_ok=True)

# Define the log file path
log_file = os.path.join(log_path, 'app.log')

# File handler with rotation
file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=3)
file_handler.suffix = '%Y%m%d'

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add file handler to the logger
Log.addHandler(file_handler)

# Change permissions of the log file to 777
os.chmod(log_file, 0o777)

# Stream handler to log to terminal
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Add stream handler to the logger
Log.addHandler(stream_handler)