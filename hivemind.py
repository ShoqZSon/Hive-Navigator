import publisher as pub
import subscriber as sub
import socket
import json


class Hivemind(pub.Publisher, sub.Subscriber):
    """The Hivemind class acts as middleman between the webserver and the bots. It is supposed to receive the tasks, store them in a queue and distribute them to the best fitting bot.
    Best fitting is determined through a comparison between the destination coordinates and the current coordinates of the bot. The closest is the best fitting.
    Hivemind is derived from Publisher and Subscriber since it needs to Publish its own queue towards the bots and Subscribe to the bots to receive the coordinates.

    Attributes
    ----------
    queue: list
        a queue of tasks (location and destination)

    Methods
    -------
    start_server()
        starts the listening-server towards the client (webserver)
    """
    queue = []
    # port and host of the server the data comes from
    def __init__(self, port='127.0.0.1', host=65432):
        """
        :param port: port of the client (webserver)
        :param host: host of the client (webserver)
        """
        super().__init__()
        self.host = '127.0.0.1'
        self.port = 65432

    def listenToConn(self):
        """This method starts listening towards the webserver (flask app) for incoming customer tasks and fills a queue with those tasks.
        This method never stops running on purpose.

        Attributes
        -----------
        -

        :return: -
        """
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


hivemind = Hivemind()
hivemind.listenToConn()

