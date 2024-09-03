import json
import queue
import time
import threading

class Bot:
    def __init__(self,id=0,level=0, hallNr=0):
        self.id = id
        self.hallNr = hallNr
        self.level = level
        self.Coordinates = {'x': 0, 'y': 0}
        self.taskQueue = queue.Queue()
        self.publish_event = threading.Event()

    def getBotData(self):
        """Pack the bot's coordinates into a JSON string."""
        data = {
            'id': self.id,
            'hall': self.hallNr,
            'level': self.level,
            'x': self.Coordinates['x'],
            'y': self.Coordinates['y']
        }
        return json.dumps(data)

    def publish_botData(self, publisher, botQueue):
        while True:
            self.publish_event.wait()
            publisher.publish(self.getBotData(),botQueue)
            self.publish_event.clear()
            time.sleep(5)

    def executeTask(self):
        while True:
            if not self.taskQueue.empty():
                task = self.taskQueue.get()
                print(f"Executing task {task}")
                for i in range(5):
                    print(f"x: {self.Coordinates['x'] + i}")
                    print(f"y: {self.Coordinates['y'] + i * 2}")
                self.taskQueue.task_done()
                self.publish_event.set()
            time.sleep(5)

    def addTask(self,task):
        self.taskQueue.put(task)
        print(f"Added task: {task} to taskQueue of bot {self.id}")

    def getId(self):
        return self.id

    def getHallNr(self):
        return self.hallNr

    def getLevel(self):
        return self.level

    def getCoordinates(self):
        return self.Coordinates

    def getTaskQueue(self):
        return self.taskQueue
