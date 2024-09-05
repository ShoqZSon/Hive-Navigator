import sys

import pika.exceptions
from publisher import Publisher
from subscriber import Subscriber
from hivemind_utility import *
import threading
import queue
import time


# Callbacks - Subscriber Functions
def from_webserver_task_callback(ch, method, properties, body) -> None:
    """Used to handle the rawTaskQueue items

    Receives the task and stores it in a local queue.

    :return: None
    """
    print("webserver_task_callback")
    task = decode_json_object(body)
    print(f"Received a new task: {task} from {method.routing_key}")

    # Enqueue the task for publishing and set the event
    task_queue.put(task)

def from_bot_callback(ch, method, properties, body) -> None:
    print("bot_callback")

    bot_data = decode_json_object(body)
    print(task_processing.is_set())
    print(initial_event.is_set())
    if not task_processing.is_set() or initial_event.is_set():
        print(f"Received {bot_data} from {method.routing_key}")
        bot_queue_dict.update({bot_data['id']:bot_data})
        print(bot_queue_dict)

        initial_event.clear()
    else:
        print("Currently processing a task, ignoring bot location update.")

def get_all_bots(ch, method, properties, body):
    bot_id = body.decode("utf-8")
    if bot_id not in bot_queue_dict:
        bot_queue_dict.update({bot_id: None})


# ---- Publisher Functions ---- #
def publish_task(publisher:Publisher) -> None:
    """The publisher publishes the best fitting task for a specific bot on bot_queue

    :param publisher: The publisher object which is to publish the task

    :return: None
    """
    while True:
        # Wait for a task to be available in the queue and removes the task from the queue when available
        task = task_queue.get()

        task_processing.set()

        bot_curr_loc = bot_queue_dict
        selected_task,bot_queue = compare_userLoc_botLoc(task,bot_curr_loc)
        publisher.publish_to_queue(message=selected_task, queue=bot_queue)
        print(f"Published task {selected_task}")

        task_processing.clear()

        task_queue.task_done()

def notify(publisher:Publisher,message='') -> None:
    """ Waits for the new_task_event to trigger. If triggered this function publishes a message on a notification_queue
    :param publisher:
    :param message: The message to be published (defaults to 'newTask')
    :return: None
    """
    while True:
        new_task_event.wait()
        try:
            if task_processing.is_set():
                print("notify queue")
                publisher.publish_to_topic(message=message,exchange='notification_topic',routing_key='notification.info')
        except (pika.exceptions.StreamLostError, pika.exceptions.AMQPChannelError) as e:
            print(f"Error during notification publishing: {e}. Reconnecting...")
            publisher.connect()  # Reconnect
        except Exception as e:
            print(f"Unexpected error during notification: {e}")
        finally:
            new_task_event.clear()

# ------------------------------- #

def check_queue():
    while True:
        if not task_queue.empty() and not task_processing.is_set():
            new_task_event.set()
        time.sleep(1)

def compare_userLoc_botLoc(usr_data:dict, bot_data:dict):
    """ The algorithm to determine which bot is the best fit for the task.
    Decides by comparing every bot_data x,y coordinate + the hall-nr with the corresponding values in usr_data

    :param usr_data:
    :param bot_data:

    :return:
    """
    print("Comparing userLoc and botLoc")
    print(f"usrLoc: {usr_data}")
    print(f"botLoc: {bot_data}")

    task = {'user': usr_data,
            'destination': {'destination': 'dest1', 'hallNr': 2, 'floor': 0, 'x': 235, 'y': 134}
            }
    task = json.dumps(task)

    myqueue = 'tasks.bot1'

    return task,myqueue

def showQueues():
    while True:
        task_items = list(task_queue.queue)
        bot_loc_items = list(bot_loc_queue.queue)
        print(f'Current Task Queue: {task_items}')
        print(f'Current Bot Location Queue: {bot_loc_items}')

        time.sleep(7)

if __name__ == '__main__':
    # queue for the tasks received by the webserver
    task_queue = queue.Queue()


    # dictionary of the bot routing_key (as key) and its data as the value
    # for distribution and keeping track of where the data comes from
    bot_queue_dict = {}

    initial_event = threading.Event()
    initial_event.set()
    # an event-trigger for sending the notifications after receiving a new task
    new_task_event = threading.Event()
    task_processing = threading.Event()

    message_broker_host = '192.168.56.106'
    message_broker_port = 5672


    # ---- Publisher & Subscriber Initialization ---- #

    # subscribes to a queue where the bots send their 'Hey I am here' notification
    sub_one_time_notification = Subscriber(message_broker_host, message_broker_port)

    # listens to the tasks coming from the webserver
    sub_webserver_task_queue = Subscriber(message_broker_host, message_broker_port)

    # listens to the coordinates(x,y), hall-nr, level of any bot that publishes to any queue "currLoc_*"
    sub_bot_curr_loc = Subscriber(message_broker_host, message_broker_port)

    # publishes a notification on the queue 'notification' to notify subscribers to publish their data
    pub_task_notification = Publisher(message_broker_host, message_broker_port)

    # publishes back to the corresponding bots with their respective task
    pub_bot_task = Publisher(message_broker_host, message_broker_port)


    # ---- Connections to RabbitMQ ---- #

    # establishes the connections
    sub_one_time_notification.connect()
    sub_webserver_task_queue.connect()
    sub_bot_curr_loc.connect()
    pub_task_notification.connect()
    pub_bot_task.connect()

    # receives an initial notification from every bot that they exist
    sub_one_time_notification.subscribe_to_queue_tmp(get_all_bots,'initial_existence_share',10)
    sub_one_time_notification.disconnect()

    bot_num = len(bot_queue_dict)
    print(f'Amount of bots is set to {bot_num}')


    # ---- Thread Area ---- #

    #show_queue_Thread = threading.Thread(target=showQueues)

    set_notification_event = threading.Thread(target=check_queue)

    # subscribe to the tasks send from the webserver (queue = 'rawTasksQueue')
    sub_webserver_task_queue_Thread = threading.Thread(target=sub_webserver_task_queue.subscribe_to_queue, args=(from_webserver_task_callback,'rawTaskQueue'))

    # subscribe to the current location data from the bots (queues = 'currLoc.*)
    sub_botCurrLoc_Thread = threading.Thread(target=sub_bot_curr_loc.subscribe_to_topic, args=(from_bot_callback,'bot_locs_topic','bot_locs','currLoc.*'))

    # publish a notification inside the queue 'notification' to the bots to notify them of new tasks
    # and trigger their publish method which sends their current location data
    pub_task_notification_Thread = threading.Thread(target=notify,args=(pub_task_notification,'newTask'))

    # publishes the tasks for specific bots on their respective queue
    pub_bot_task_Thread = threading.Thread(target=publish_task, args=(pub_bot_task,))

    # publishes the coordinates of the chosen bot back to the webserver/client periodically
    # ...put here...

    # starts the threads
    #show_queue_Thread.start()

    sub_webserver_task_queue_Thread.start()
    sub_botCurrLoc_Thread.start()
    pub_task_notification_Thread.start()
    pub_bot_task_Thread.start()

    # closes the threads gracefully
    #show_queue_Thread.join()

    sub_webserver_task_queue_Thread.join()
    sub_botCurrLoc_Thread.join()
    pub_task_notification_Thread.join()
    pub_bot_task_Thread.join()


    # ---- Closing the RabbitMQ connections ---- #

    # closes the connection to RabbitMQ
    sub_webserver_task_queue.disconnect()
    sub_bot_curr_loc.disconnect()
    pub_task_notification.disconnect()
    pub_bot_task.disconnect()