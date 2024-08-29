import publisher as p
import subscriber as s
import socket
import json


class Hivemind(p.Publisher, s.Subscriber):
    # port and host of the server the data comes from
    def __init__(self, port, host):
        super().__init__()
        self.host = '127.0.0.1'
        self.port = 65432
        self.queue = []


    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server listening on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    data = conn.recv(1024)
                    if data:
                        # Decode and parse the JSON data
                        received_data = json.loads(data.decode())
                        print(f"Received data: {received_data}")
                        self.queue.append(received_data)
                        print(self.queue)

                        # Send a positive acknowledgment back to the client
                        conn.sendall(b"200")
                    else:
                        print("No data received.")


hivemind = Hivemind("bla","blub")
hivemind.start_server()

