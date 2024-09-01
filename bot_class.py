from publisher import Publisher
from subscriber import Subscriber
import json
import time

class Bot(Publisher, Subscriber):
    def __init__(self, messageBrokerHost, messageBrokerPort, level=0, hall=0):
        Publisher.__init__(self, host=messageBrokerHost, port=messageBrokerPort, routing_key='currLoc')
        Subscriber.__init__(self, host=messageBrokerHost, port=messageBrokerPort, queue='taskQueue')

        self.hall = hall
        self.level = level
        self.ownCoordinates = {'x': 0, 'y': 0}

    def packData(self):
        """Pack the bot's coordinates into a JSON string."""
        data = {
            'hall': self.hall,
            'level': self.level,
            'x': self.ownCoordinates['x'],
            'y': self.ownCoordinates['y']
        }
        return json.dumps(data)

    def publish_coordinates(self):
        """Publish the bot's coordinates to the messageBroker."""
        self.connect()
        message = self.packData()
        self.publish(message)
        self.close()

    def task_callback(self, ch, method, properties, body):
        """Handle tasks received from the messageBroker."""
        task = json.loads(body)
        print(f" [x] Received task: {task}")
        # Process the task here
        for i in range(3):
            self.drive()
            time.sleep(0.5)

    def start_listening_for_tasks(self):
        """Start listening for tasks from the hivemind."""
        self.connect()
        self.start_consuming(callback=self.task_callback)

    def drive(self):
        print("Driving...")