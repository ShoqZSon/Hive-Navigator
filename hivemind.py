import sys

import pika.exceptions
from publisher import Publisher
from subscriber import Subscriber
from hivemind_utility import *
import threading
import queue


# Callbacks - Subscriber Functions
def from_webserver_task_callback(ch, method, properties, body) -> None:
    """Used to handle the rawTaskQueue items

    Receives the raw task (jsonObject), decodes that with decode_json_object(body) into its correct dictionary form.
    Puts the task into the task_queue and sets an event-trigger for the function to send the task as well as
    sending a notification towards the bots.

    :return: None
    """
    print("webserver_task_callback")
    task = decode_json_object(body)
    print(f"Received {task} from {method.routing_key}")

    # Enqueue the task for publishing and set the event
    task_queue.put(task)

    # sets an event to trigger the publishing of the notification that a new
    new_task_Event.set()

def from_bot_callback(ch, method, properties, body) -> None:
    print("bot_callback")
    task = decode_json_object(body)
    print(f"Received {task} from {method.routing_key}")


# ---- Publisher Functions ---- #
def publish_task(publisher,bot_curr_loc,bot_queue) -> None:
    """The publisher publishes the best fitting task for a specific bot on bot_queue
    :param publisher: The publisher object which is to publish the task
    :param bot_curr_loc: An array of bot locations for comparison
    :param bot_queue: The queue to send the task to
    :return: None
    """
    while True:
        # Wait for a task to be available in the queue
        # removes the task from the queue when available
        task = task_queue.get()

        selected_task = compare_userLoc_botLoc(task,bot_curr_loc)
        publisher.publish(selected_task, queue=bot_queue)
        print(f"Published task {selected_task}")

        task_queue.task_done()

        new_task_Event.clear()

def compare_userLoc_botLoc(usr_data:dict, bot_data:dict) -> dict:
    """ The algorithm to determine which bot is the best fit for the task.
    Decides by comparing every bot_data x,y coordinate + the hall-nr with the corresponding values in usr_data

    :param usr_data:
    :param bot_data:
    :return:
    """
    print("Comparing userLoc and botLoc")
    print(f"usrLoc: {usr_data}")
    print(f"botLoc: {bot_data}")

    return {}

def notify(publisher:Publisher,message='') -> None:
    """ Waits for the newTask_event to trigger. If triggered this function publishes a message on a notification_queue
    :param publisher:
    :param message: The message to be published (defaults to 'newTask')
    :return: None
    """
    while True:
        new_task_Event.wait()
        try:
            print("notify queue")
            publisher.publish_to_topic(message=message,exchange='notification_topic',routing_key='notification.info')
        except (pika.exceptions.StreamLostError, pika.exceptions.AMQPChannelError) as e:
            print(f"Error during notification publishing: {e}. Reconnecting...")
            publisher.connect()  # Reconnect
        except Exception as e:
            print(f"Unexpected error during notification: {e}")
        finally:
            new_task_Event.clear()

if __name__ == '__main__':
    # queue for the tasks received by the webserver
    task_queue = queue.Queue()

    # an event-trigger for the
    new_task_Event = threading.Event()

    message_broker_host = '192.168.56.106'
    message_broker_port = 5672


    # ---- Publisher & Subscriber Initialization ---- #

    # listens to the tasks coming from the webserver
    sub_webserver_task_queue = Subscriber(message_broker_host, message_broker_port)

    # listens to the coordinates(x,y), hall-nr, level of any bot that publishes to any queue "currLoc_*"
    sub_bot_curr_loc = Subscriber(message_broker_host, message_broker_port)

    # publishes a notification on the queue 'notification' to notify subscribers to publish their data
    pub_task_notification = Publisher(message_broker_host, message_broker_port)

    # publishes back to the corresponding bots with their respective task
    #pub_bot_task = Publisher()

    # ---- Connections to RabbitMQ ---- #

    # establishes the connections
    sub_webserver_task_queue.connect()
    sub_bot_curr_loc.connect()
    pub_task_notification.connect()
    #pub_botTasks.connect()

    # ---- Thread Area ---- #

    # subscribe to the tasks send from the webserver (queue = 'rawTasksQueue')
    sub_webserver_task_queue_Thread = threading.Thread(target=sub_webserver_task_queue.subscribe_to_queue, args=(from_webserver_task_callback,'rawTaskQueue'))

    # subscribe to the current location data from the bots (queue = 'currLoc.*)
    sub_botCurrLoc_Thread = threading.Thread(target=sub_bot_curr_loc.subscribe_to_topic, args=(from_bot_callback,'bot_locs_topic','bot_locs','currLoc.*'))

    # publish a notification inside the queue 'notification' to the bots to notify them of new tasks
    # and trigger their publish method which sends their current location data
    pub_task_notification_Thread = threading.Thread(target=notify,args=(pub_task_notification,'newTask'))

    # publishes the tasks for specific bots on their respective queue (pattern = currLoc.*; * -> bot1,bot2,...)
    #pub_botTasks_Thread = threading.Thread(target=publish_task, args=(pub_botTasks,sub_botCurrLoc,'currLoc.'))

    # publishes the coordinates of the chosen bot back to the webserver/client periodically
    # ...put here...

    # starts the threads
    sub_webserver_task_queue_Thread.start()
    sub_botCurrLoc_Thread.start()
    pub_task_notification_Thread.start()
    #pub_botTasks_Thread.start()

    # closes the threads gracefully
    sub_webserver_task_queue_Thread.join()
    sub_botCurrLoc_Thread.join()
    pub_task_notification_Thread.join()
    #pub_botTasks_Thread.join()

    # ---- Closing the RabbitMQ connections ---- #

    # closes the connection to RabbitMQ
    sub_webserver_task_queue.close()
    sub_bot_curr_loc.close()
    pub_task_notification.close()
    #pub_botTasks.close()