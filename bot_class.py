import json
import queue
import time
import threading
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.srv import NavigateToPose

class Bot(Node):
    def __init__(self,bot_id=0,floor=0, hallNr=0):
        """

        :param bot_id:
        :param floor:
        :param hallNr:
        state: 0 = idle, 1 on the job, 2 back to source # WIP on the naming
        """
        super().__init__('bot_node')
        self.id = bot_id
        self.hallNr = hallNr
        self.floor = floor
        self.coordinates = {'x': 0, 'y': 0}
        self.state = 0
        self.taskQueue = queue.Queue()
        self.publish_event = threading.Event()
        self.execute_event = threading.Event()
        rclpy.init()

    def getBotData(self):
        """Pack the bot's nates into a JSON string."""
        data = {
            'id': self.id,
            'hall': self.hallNr,
            'floor': self.floor,
            'x': self.coordinates['x'],
            'y': self.coordinates['y'],
            'state': self.state
        }
        return json.dumps(data)

    def notificationCallback(self, ch, method, properties, body):
        self.publish_event.set()

    def publishBotData(self, publisher):
        while True:
            self.publish_event.wait()

            botData = self.getBotData()
            print("publishing the bot data now")
            publisher.publish_to_topic(botData,'bot_locs_topic',f'currLoc.{self.getId()}')

            time.sleep(1)

            self.publish_event.clear()

    def addTask_callback(self,ch, method, properties, body):
        task = json.loads(body)
        if task not in self.taskQueue.queue:
            self.taskQueue.put(task)
            print(f"Added task: {task} to taskQueue of bot {self.id}")
            self.execute_event.set()

    def executeTask(self):
        while True:
            self.execute_event.wait()
            task = self.taskQueue.get()
            self.state = 1

            x = task['x']
            y = task['y']

            self.set_navigation_goal(x,y)

            self.taskQueue.task_done()

            self.execute_event.clear()
            self.state = 0
            time.sleep(1)

    def set_navigation_goal(self, x, y):
        request = NavigateToPose.Request()
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.orientation.w = 1.0

        request.pose = goal_pose
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info(f'Goal set to x: {x}, y: {y} successfully!')
        else:
            self.get_logger().error('Failed to set goal')

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
