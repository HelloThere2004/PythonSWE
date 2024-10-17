import socket
import time

# Server address and port
host = "localhost"
port = 23304

# Message to be sent
message = "#860186054704537#MT700#0000#AUTO#1\r\n#36$GPRMC,082947.00,A,1046.6411,N,10640.8207,E,8.50,121.40,071024,,,A*5A\r\n##\r\n"

def send_message():
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # Connect to the server
            s.connect((host, port))
            # Send the message
            s.sendall(message.encode())
            print(f"Message sent to {host}:{port}")
        except Exception as e:
            print(f"Failed to send message: {e}")

def main():

    send_message()
 # Wait for 10 seconds before sending the next message

if __name__ == "__main__":
    main()
