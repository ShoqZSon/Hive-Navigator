import socket
import json


def send_data(location, destination, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        # Create a dictionary with location and destination
        data = {
            "location": location,
            "destination": destination
        }

        # Convert the dictionary to a JSON string
        message = json.dumps(data)

        # Send the JSON string to the server
        s.sendall(message.encode())

        # Receive response from the server
        data = s.recv(1024)
        print(f"Received {data.decode()} from server")

        if data.decode() == "200":
            print("Closing connection.")