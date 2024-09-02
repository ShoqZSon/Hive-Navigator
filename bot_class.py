import json
import queue
import time

class Bot:
    def __init__(self,id=0,level=0, hallNr=0):
        self.id = id
        self.hallNr = hallNr
        self.level = level
        self.Coordinates = {'x': 0, 'y': 0}
        self.taskQueue = queue.Queue()

    def getPackedData(self):
        """Pack the bot's coordinates into a JSON string."""
        data = {
            'id': self.id,
            'hall': self.hallNr,
            'level': self.level,
            'x': self.Coordinates['x'],
            'y': self.Coordinates['y']
        }
        return json.dumps(data)

    def executeTask(self):
        if self.taskQueue.empty():
            print("Task queue is empty")
        else:
            task = self.taskQueue.get()
            print(f"Executing task {task}")
            for i in range(5):
                print(f"x: {self.Coordinates['x'] + i}")
                print(f"y: {self.Coordinates['y'] + i * 2}")
            self.taskQueue.task_done()

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
