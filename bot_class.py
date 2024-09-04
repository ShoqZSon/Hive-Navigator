import json
import queue
import time
import threading

class Bot:
    def __init__(self,bot_id=0,floor=0, hallNr=0):
        self.id = bot_id
        self.hallNr = hallNr
        self.floor = floor
        self.Coordinates = {'x': 0, 'y': 0}
        self.taskQueue = queue.Queue()
        self.publish_event = threading.Event()
        self.last_published_time = 0

    def getBotData(self):
        """Pack the bot's coordinates into a JSON string."""
        data = {
            'id': self.id,
            'hall': self.hallNr,
            'floor': self.floor,
            'x': self.Coordinates['x'],
            'y': self.Coordinates['y']
        }
        return json.dumps(data)

    def publishBotData(self, publisher, cooldown_seconds=5):
        while True:
            self.publish_event.wait()

            current_time = time.time()

            time_elapsed = current_time - self.last_published_time

            if time_elapsed >= cooldown_seconds:
                botData = self.getBotData()
                publisher.publish_to_topic(botData,'bot_locs_topic',f'currLoc.{self.getId()}')

            time.sleep(1)

            self.publish_event.clear()

    def executeTask(self):
        if not self.taskQueue.empty():
            while True:
                task = self.taskQueue.get()
                print(f"Executing task {task}")
                for i in range(5):
                    print(f"x: {self.Coordinates['x'] + i}")
                    print(f"y: {self.Coordinates['y'] + i * 2}")
                self.taskQueue.task_done()
                time.sleep(5)

    def notificationCallback(self, ch, method, properties, body):
        if body.decode() == 'newTask':
            self.publish_event.set()

    def addTask(self,task):
        self.taskQueue.put(task)
        print(f"Added task: {task} to taskQueue of bot {self.id}")

    def getId(self):
        return self.id

    def getHallNr(self):
        return self.hallNr

    def getFloor(self):
        return self.floor

    def getCoordinates(self):
        return self.Coordinates

    def getTaskQueue(self):
        return self.taskQueue
