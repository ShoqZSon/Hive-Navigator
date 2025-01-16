import json
import queue
import time
import threading
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Odometry


class Bot(Node):
    def __init__(self, bot_id=0, floor=0, hallNr=0, x=0, y=0):
        """
        Initialize the Bot instance.

        Parameters:
        ----------
        bot_id : int
            Unique ID for the bot.
        floor : int
            Floor number where the bot operates.
        hallNr : int
            Hall number where the bot operates.
        x : float
            Initial X coordinate.
        y : float
            Initial Y coordinate.
        """
        # Initialize ROS2
        rclpy.init()

        # Initialize bot attributes
        self.id = bot_id
        self.hallNr = hallNr
        self.floor = floor
        self.coordinates = {'x': x, 'y': y}  # Initial coordinates
        self.state = 0  # Bot state: 0 = idle, 1 = on the job, 2 = returning to source
        self.taskQueue = queue.Queue()
        self.currentTask = None
        self.taskCount = 0  # Number of tasks handled in the current session
        self.publish_event = threading.Event()
        self.execute_event = threading.Event()
        self.action_client_name = f'{bot_id}_nav2pose'

        # Initialize ROS2 node
        super().__init__(f'{bot_id}_node')

        # Create an action client for NavigateToPose
        self._navigate_action_client = ActionClient(self, NavigateToPose, self.action_client_name)

        # Subscribe to the /odom topic to receive real-time odometry updates
        self.create_subscription(Odometry, '/odom', self.odometry_callback, 10)

        # Log the initialization
        self.get_logger().info(f'[{self.id}] Bot initialized and started publishing coordinates.')

    def odometry_callback(self, msg):
        """
        Callback function to handle odometry updates.

        Parameters:
        ----------
        msg : Odometry
            Message containing the robot's current position and velocity.
        """
        # Update the bot's current coordinates from the odometry message
        self.coordinates['x'] = msg.pose.pose.position.x
        self.coordinates['y'] = msg.pose.pose.position.y

        # Log the updated coordinates for monitoring
        self.get_logger().info(f'[{self.id}] Updated coordinates: {self.coordinates}')

    def getBotData(self):
        """
        Pack the bot's data into a JSON string.

        Returns:
        -------
        str
            JSON string containing the bot's data.
        """
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
        """
        Callback to handle incoming notifications.
        Sets the event to trigger data publishing.

        Parameters:
        ----------
        ch : Channel
            Channel from which the notification was received.
        method : Method
            Method information.
        properties : Properties
            Message properties.
        body : bytes
            Notification payload.
        """
        self.publish_event.set()  # Signal to publish bot data

    def publishBotData(self, publisher):
        """
        Continuously publish the bot's data to a topic when signaled.
        This runs in a separate thread.

        Parameters:
        ----------
        publisher : Publisher
            The publisher object used to send data.
        """
        while True:
            # Wait for the signal to publish data
            self.publish_event.wait()

            # Prepare the bot data for publishing
            botData = self.getBotData()
            print(f'[{self.id}] Publishing the bot data now')

            # Publish the data to the specified topic
            publisher.publishToTopic(botData, 'bot_locs_topic', f'currLoc.{self.getId()}')

            # Sleep to avoid spamming the topic
            time.sleep(1)

            # Clear the signal to wait for the next event
            self.publish_event.clear()

    def addTaskCallback(self, ch, method, properties, body):
        """
        Callback to add a task to the bot's queue.

        Parameters:
        ----------
        ch : Channel
            Channel from which the task was received.
        method : Method
            Method information.
        properties : Properties
            Message properties.
        body : bytes
            Task payload in JSON format.
        """
        # Parse the task from the received message
        task = json.loads(body)

        # Add the task to the queue if it is not already present
        if task not in self.taskQueue.queue:
            self.taskQueue.put(task)
            print(f'[{self.id}] Added task: {task} to taskQueue of {self.id}')

            # Signal to execute the task
            self.execute_event.set()

    def executeTask(self):
        """
        Continuously execute tasks from the queue when signaled.
        This runs in a separate thread.
        """
        while True:
            # Wait for the signal to execute a task
            self.execute_event.wait()

            # Get the next task from the queue
            task = self.taskQueue.get()
            self.currentTask = task
            print(f'[{self.id}] Executing task: {self.currentTask}')
            self.state = 1  # Update state to "on the job"

            # Extract the destination coordinates from the task
            dest_x = float(task['destination'].split(',')[-2])
            dest_y = float(task['destination'].split(',')[-1])

            # Set the navigation goal
            print(f'[{self.id}] Setting the navigation goal: [{dest_x}, {dest_y}]')
            self.setNavigationGoal(dest_x, dest_y)

            # Mark the task as done
            print(f'[{self.id}] Task done')
            self.taskQueue.task_done()

            # Clear the signal and reset state
            self.execute_event.clear()
            self.state = 0
            time.sleep(0.5)

    def setNavigationGoal(self, x, y):
        """
        Send a navigation goal to the NavigateToPose action server.

        Parameters:
        ----------
        x : float
            X-coordinate of the goal.
        y : float
            Y-coordinate of the goal.
        """
        # Create a PoseStamped message for the goal
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.orientation.w = 1.0  # Facing forward

        # Create the goal message
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = goal_pose

        # Wait for the action server to be available
        self._navigate_action_client.wait_for_server()
        self.get_logger().info(f'[{self.id}] Sending goal to NavigateToPose action server...')

        # Send the goal asynchronously
        future = self._navigate_action_client.send_goal_async(goal_msg)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """
        Callback to handle the response from the NavigateToPose action server.

        Parameters:
        ----------
        future : Future
            The future object representing the goal response.
        """
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error(f'[{self.id}] Navigation goal was rejected!')
            return

        self.get_logger().info(f'[{self.id}] Navigation goal accepted. Waiting for result...')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        """
        Callback to handle the result of the navigation action.

        Parameters:
        ----------
        future : Future
            The future object representing the result.
        """
        result = future.result().result
        self.get_logger().info(f'[{self.id}] Navigation completed with result: {result}')
