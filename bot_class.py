import json
import queue
import time
import threading

class Bot:
    def __init__(self,bot_id=0,floor=0, hallNr=0):
        """

        :param bot_id:
        :param floor:
        :param hallNr:
        state: 0 = idle, 1 on the job, 2 back to source # WIP on the naming
        """
        self.id = bot_id
        self.hallNr = hallNr
        self.floor = floor
        self.Coordinates = {'x': 0, 'y': 0}
        self.state = 0
        self.taskQueue = queue.Queue()
        self.publish_event = threading.Event()
        self.execute_event = threading.Event()

    def getBotData(self):
        """Pack the bot's coordinates into a JSON string."""
        data = {
            'id': self.id,
            'hall': self.hallNr,
            'floor': self.floor,
            'x': self.Coordinates['x'],
            'y': self.Coordinates['y'],
            'state': self.state
        }
        return json.dumps(data)

    def publishBotData(self, publisher):
        while True:
            self.publish_event.wait()

            botData = self.getBotData()
            print("publishing the bot data now")
            publisher.publish_to_topic(botData,'bot_locs_topic',f'currLoc.{self.getId()}')

            time.sleep(1)

            self.publish_event.clear()

    def executeTask(self):
        while True:
            self.execute_event.wait()
            print(self.taskQueue)
            task = self.taskQueue.get()
            self.state = 1
            print(f"Executing task {task}")
            for i in range(20):
                print(f'(x: {self.Coordinates["x"] + i};y: {self.Coordinates["y"] + i * 2})')
                time.sleep(2)
            self.taskQueue.task_done()

            self.execute_event.clear()
            self.state = 0
            time.sleep(1)

    def notificationCallback(self, ch, method, properties, body):
        self.publish_event.set()

    def addTask_callback(self,ch, method, properties, body):
        task = json.loads(body)
        if task not in self.taskQueue.queue:
            self.taskQueue.put(task)
            print(f"Added task: {task} to taskQueue of bot {self.id}")
            self.execute_event.set()

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

    def getState(self):
        return self.state
