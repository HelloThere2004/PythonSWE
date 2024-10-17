import logging
from datetime import datetime
import os


def setup_logging(log_dir="logs"):
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a valid filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"mtrack-tcp-application-{timestamp}.log"
    log_path = os.path.join(log_dir, log_filename)

    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )
    handler = logging.FileHandler(log_path)
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs
    logger.addHandler(handler)
    return log_path
