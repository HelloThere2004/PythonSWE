import os
import logging
import threading
from src.config.logger import setup_logging
from src.tcp_receivers.mtrack_receiver import create_tcp_receiver
from src.controllers.mtrack_data_parser import process_message

log_filename = setup_logging()

def start_tcp_receiver():
    tcp_receiver = create_tcp_receiver(process_message)
    tcp_receiver.start()

if __name__ == "__main__":
    logging.info("Initializing application")

    # Start TCP receiver in a separate thread
    tcp_thread = threading.Thread(target=start_tcp_receiver)
    tcp_thread.start()

    logging.info("TCP receiver started in a separate thread")

    try:
        # Keep the main thread running
        tcp_thread.join()
    except KeyboardInterrupt:
        logging.info("Application terminated by user")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("Application shutting down")
