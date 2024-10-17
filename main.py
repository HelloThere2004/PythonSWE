import os
import logging

from src.config.logger import setup_logging

log_filename = setup_logging()

if __name__ == "__main__":
    logging.info("initialize")
