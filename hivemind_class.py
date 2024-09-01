from publisher import Publisher
from subscriber import Subscriber
import socket
import json


class Hivemind(Publisher,Subscriber):
    """The Hivemind class acts as middleman between the webserver and the bots. It is supposed to receive the tasks, store them in a queue and distribute them to the best fitting bot.
    Best fitting is determined through a comparison between the destination coordinates and the current coordinates of the bot. The closest is the best fitting.
    Hivemind is derived from Publisher and Subscriber since it needs to Publish its own queue towards the bots and Subscribe to the bots to receive the coordinates.

    Attributes
    ----------
    queue: list
        a queue of tasks (location and destination)

    Methods
    -------
    listenToConn()
        starts the listening-server towards the client (webserver)
    """
    def __init__(self, messageBrokerHost, messageBrokerPort,webserverHost, webserverPort):
        Publisher.__init__(self, host=messageBrokerHost, port=messageBrokerPort, routing_key='taskQueue')
        Subscriber.__init__(self, host=messageBrokerHost, port=messageBrokerPort, queue='currLoc')
        self.webserverHost = webserverHost
        self.webserverPort = webserverPort
        self.taskQueue = []
        self.listenhost = '192.168.56.104'
        self.listenport = 65432

    def listenToConn(self):
        """This method starts listening towards the webserver (flask app) for incoming customer tasks and fills a queue with those tasks.
        This method never stops running on purpose.
        Its whole purpose is to fill the task queue.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.listenhost, self.listenport))
            s.listen()
            print(f"Server listening on {self.listenhost}:{self.listenport}")

            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    data = conn.recv(1024)
                    if data:
                        # Decode and parse the JSON data
                        received_data = json.loads(data.decode())
                        print(f"Received data: {received_data}")

                        self.taskQueue.append(received_data)
                        print(f"Current queue: {self.taskQueue}")

                        # Send a positive acknowledgment back to the client
                        conn.sendall(b"200")
                    else:
                        print("No data received.")

    def create_task(self, task):
        """Create a new task for the bots."""
        return json.dumps(task)

    def publish_task(self, task):
        """Publish a task to the bots."""
        self.connect()
        message = self.create_task(task)
        self.publish(message)
        self.close()

    def location_callback(self, ch, method, properties, body):
        """Handle incoming location data from bots."""
        location_data = json.loads(body)
        print(f" [x] Received location data: {location_data}")

        # Process location data here
        self.compare_task_and_bot(self.taskQueue[0], location_data)

    def start_listening_for_locations(self):
        """Start listening for location data from bots."""
        self.connect()
        self.start_consuming(callback=self.location_callback)

    def compare_task_and_bot(self, taskLoc, botLoc):
        print(f"Comparing {taskLoc} with {botLoc}")
        print("Choosing the best fitting task..")
