import socket
import select
import logging
import threading

logger = logging.getLogger(__name__)

class TCPReceiver:
    def __init__(self, host='0.0.0.0', port=23304, message_handler=None):
        self.host = host
        self.port = port
        self.message_handler = message_handler
        self.socket = None
        self.running = False

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        self.running = True
        logger.info(f"TCP Server listening on {self.host}:{self.port}")

        while self.running:
            try:
                conn, addr = self.socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()
            except Exception as e:
                logger.error(f"An error occurred in the server: {e}")

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
        logger.info("TCP Server stopped")

    def handle_client(self, conn, addr):
        logger.info(f"Connected by {addr}")
        while self.running:
            try:
                ready = select.select([conn], [], [], 60)
                if ready[0]:
                    data = conn.recv(1024)
                    if not data:
                        logger.info(f"Connection closed by {addr}")
                        break

                    message = data.decode('utf-8').strip()
                    logger.info(f"Received message: {message}")

                    if self.message_handler:
                        self.message_handler(message)

                    # Send a minimal acknowledgment
                    conn.sendall(b'\x06')  # ASCII ACK character
            except Exception as e:
                logger.error(f"Error handling client {addr}: {e}")
                break

        conn.close()
        logger.info(f"Connection with {addr} closed.")

def create_tcp_receiver(message_handler):
    return TCPReceiver(message_handler=message_handler)
