import os
import logging
import threading
from gevent.pywsgi import WSGIServer
from src.config.logger import setup_logging
from src.tcp_receivers.mtrack_receiver import create_tcp_receiver
from src.controllers.mtrack_data_parser import process_message
from src.restapi.mtrack_api import app

log_filename = setup_logging()

def start_tcp_receiver():
    tcp_receiver = create_tcp_receiver(process_message)
    tcp_receiver.start()

def start_flask_api():
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()

def user_input_handler():
    while True:
        command = input("Application running... TCP listening at port 23304. REST API running on port 5000.\n").strip().lower()
        if command == "help":
            print("Available commands: help, exit")
        elif command == "exit":
            logging.info("Exiting application...")
            os._exit(0)
        else:
            print("Invalid command. Enter help for more information.")

if __name__ == "__main__":
    logging.info("Initializing application")

    # Start TCP receiver in a separate thread
    tcp_thread = threading.Thread(target=start_tcp_receiver)
    tcp_thread.start()

    logging.info("TCP receiver started in a separate thread")

    # Start Flask API in a separate thread
    api_thread = threading.Thread(target=start_flask_api)
    api_thread.start()

    logging.info("Flask API started in a separate thread")

    input_thread = threading.Thread(target=user_input_handler, daemon=True)
    input_thread.start()

    try:
        # Keep the main thread running
        tcp_thread.join()
        api_thread.join()
    except KeyboardInterrupt:
        logging.info("Application terminated by user")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("Application shutting down")
