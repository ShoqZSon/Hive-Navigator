import json
import queue
import time
import threading
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose

class Bot(Node):
    def __init__(self,bot_id=0,floor=0, hallNr=0,x=0,y=0):
        """

        Parameters
        ----------
        bot_id
        floor
        hallNr

        state -> 0 = idle, 1 on the job, 2 back to source # WIP on the naming
        """
        rclpy.init()

        self.id = bot_id
        self.hallNr = hallNr
        self.floor = floor
        self.coordinates = {'x': x, 'y': y}
        self.state = 0
        self.taskQueue = queue.Queue()
        self.currentTask = None
        self.taskCount = 0 # count for the current session, does not get saved permanently
        self.publish_event = threading.Event()
        self.execute_event = threading.Event()
        self.action_client_name = f'{bot_id}_nav2pose'

        super().__init__(f'{bot_id}_node')

        # Action client for NavigateToPose
        self._navigate_action_client = ActionClient(self, NavigateToPose, self.action_client_name)

    def getBotData(self):
        """Pack the bot's data into a JSON string."""
        data = {
            'id': self.id,
            'hall': self.hallNr,
            'floor': self.floor,
            'x': self.coordinates['x'],
            'y': self.coordinates['y'],
            'state': self.state,
            'currentTask': self.currentTask,
            'taskCount': self.taskCount
        }
        return json.dumps(data)

    def notificationCallback(self, ch, method, properties, body):
        self.publish_event.set()

    def publishBotData(self, publisher):
        while True:
            self.publish_event.wait()

            botData = self.getBotData()
            print(f'[{self.id}] publishing the bot data now')
            publisher.publishToTopic(botData,'bot_locs_topic',f'currLoc.{self.getId()}')

            time.sleep(1)

            self.publish_event.clear()

    def addTaskCallback(self,ch, method, properties, body):
        task = json.loads(body)
        if task not in self.taskQueue.queue:
            self.taskQueue.put(task)
            print(f'[{self.id}] Added task: {task} to taskQueue of {self.id}')
            self.execute_event.set()

    def executeTask(self):
        while True:
            self.execute_event.wait()
            task = self.taskQueue.get()
            self.currentTask = task
            print(f'[{self.id}] Executing task: {self.currentTask}')
            self.state = 1

            dest_x = task['destination'].split(',')[-2]
            dest_y = task['destination'].split(',')[-1]

            print(f'[{self.id}] Setting the navigation goal: [{dest_x},{dest_y}]')
            self.setNavigationGoal(dest_x,dest_y)

            print(f'[{self.id}] Task done')
            self.taskQueue.task_done()

            self.execute_event.clear()
            self.state = 0
            time.sleep(0.5)

    def setNavigationGoal(self, x, y):
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.orientation.w = 1.0

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = goal_pose

        self._navigate_action_client.wait_for_server()
        self.get_logger().info(f'[{self.id}] Sending goal to NavigateToPose action server...')

        future = self._navigate_action_client.send_goal_async(goal_msg)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error(f'[{self.id}] Navigation goal was rejected!')
            return

        self.get_logger().info(f'[{self.id}] Navigation goal accepted. Waiting for result...')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'[{self.id}] Navigation completed with result: {result}')

    def getId(self):
        return self.id

    def getHallNr(self):
        return self.hallNr

    def getFloor(self):
        return self.floor

    def getCoordinates(self):
        return self.coordinates

    def getTaskQueue(self):
        return self.taskQueue

    def getState(self):
        return self.state

    def setXY(self,x,y):
        self.coordinates['x'] = x
        self.coordinates['y'] = y

