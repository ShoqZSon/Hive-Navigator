import socket
import json


def sendDataTo(location, destination, host, port):
    """Sends the data (location and destination) in json format towards the host and port

    Arguments
    ---------
        location: str
            location of the terminal the customer sent the task from
        destination: str
            desired destination of the customer
        host: str
            host address of the hivemind
        port: int
            port of the hivemind

    Format of the data:
            data = {
                "location": str,
                "destination": str
            }

    After sending we receive a response.

    :returns -
    """
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
        response = s.recv(1024)
        print(f"Received {response.decode()} from server")

        if response.decode() == "success":
            print("Data sent successfully")
            print("Closing connection.")