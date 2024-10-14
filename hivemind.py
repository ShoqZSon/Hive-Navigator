import sys
import pika.exceptions
from publisher import Publisher
from subscriber import Subscriber
from hivemind_utility import *
import threading
import queue
import time
from compareAlgorithm import *

# ---- Global Variables ---- #
bot_num = 0
bot_queue_lock = threading.Lock()  # For protecting shared resources like thread_count
bot_data_event = threading.Event()  # Event to signal that all bots have reported in

# Callbacks - Subscriber Functions
def from_webserver_task_callback(ch, method, properties, body):
    """
    Processes the incoming tasks.
    Receives the task and stores it in a local queue.

    Parameters
    ----------
    ch
    method
    properties
    body

    Returns
    -------

    """
    print("webserver_task_callback")
    task = decodeJsonObject(body)
    print(f"Received a new task: [{task}] from [{method.routing_key}]")

    # Enqueue the task for publishing
    task_queue.put(task)

    # triggers the event that a new task has been received
    new_task_event.set()

def from_bot_callback(ch, method, properties, body) -> None:
    """
    Processes the data the bots have sent data into the queue.
    This function checks for the correct state. If its in idle (0) or back-to-source (2), the current bot data gets updated in bot_data (dictionary).
    If its on-the-job (1) the current bot data of this bot gets updated to None.

    Parameters
    ----------
    ch
    method
    properties
    body

    Returns
    -------

    """
    print("bot_callback")

    bot_data = decodeJsonObject(body)
    print(f'Received new bot data: [{bot_data}] from [{method.routing_key}]')
    with bot_queue_lock:
        if bot_data['state'] == 0 or bot_data['state'] == 2:
            bot_queue_dict.update({bot_data['id']:bot_data})
        else:
            print(f'bot is being ignored due to its state: [{bot_data["state"]}]')
            bot_queue_dict.update({bot_data['id']:None})
        print(bot_queue_dict)

    # if the size of the dictionary is equal to the amount of registered bots the event sets
    # which triggers
    if len(bot_queue_dict) == bot_num:
        bot_data_event.set()

def get_all_bots(ch, method, properties, body):
    bot_data = decodeJsonObject(body)
    bot_id = bot_data['id']

    if bot_id not in bot_queue_dict:
        bot_queue_dict.update({bot_id: bot_data})

# ---- Publisher Functions ---- #
def publish_task(publisher:Publisher) -> None:
    """The publisher publishes the best fitting task for a specific bot on bot_queue

    :param publisher: The publisher object which is to publish the task

    """
    while True:
        print("publish_task")
        while True:
            # Wait for a task to be available in the queue and removes the task from the queue when available
            task = task_queue.get()
            # waits for the bot_data_event.set() in "from_bot_callback"
            # this triggers the processing of the new task
            bot_data_event.wait()

            with bot_queue_lock:
                    bot_curr_loc = bot_queue_dict.copy()
                    selected_task,bot_queue = compareUserLocBotLoc(task,bot_curr_loc)

            selected_task = json.dumps(selected_task)

            print(f'Published selected task [{selected_task}] to [{bot_queue}]')
            publisher.publishToQueue(message=selected_task, queue=bot_queue)

            task_queue.task_done()

            bot_data_event.clear()

def notify(publisher:Publisher,message=''):
    """
    Waits for the new_task_event to trigger. If triggered this function publishes a message on a notification_queue

    Parameters
    ----------
    publisher
    message - The message to be published (defaults to 'newTask')

    Returns
    -------

    """
    while True:
        new_task_event.wait()
        try:
            print("Notifying the bots")
            publisher.publishToTopic(message=message,exchange='notification_topic',routing_key='notification.info')
        except (pika.exceptions.StreamLostError, pika.exceptions.AMQPChannelError) as e:
            print(f"Error during notification publishing: {e}. Reconnecting...")
            publisher.connect()  # Reconnect
        except Exception as e:
            print(f"Unexpected error during notification: {e}")
        finally:
            new_task_event.clear()

# ------------------------------- #

def check_queue():
    """Periodically checks and prints the task queue and bot queue status."""
    while True:
        with bot_queue_lock:
            task_items = list(task_queue.queue)
            bot_items = list(bot_queue_dict.items())
        print(f'Current Task Queue: {task_items}')
        print(f'Current Bot Data: {bot_items}')
        time.sleep(5)

if __name__ == '__main__':
    # queue for the tasks received by the webserver
    task_queue = queue.Queue()

    # dictionary of the bot routing_key (as key) and its data as the value
    # for distribution and keeping track of where the data comes from
    bot_queue_dict = {}

    # an event-trigger for sending the notifications after receiving a new task
    new_task_event = threading.Event()
    thread_count = 0

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
    sub_one_time_notification.subscribeToQueueTmp(get_all_bots,'registration')
    sub_one_time_notification.disconnect()

    bot_num = len(bot_queue_dict) # amount of bots available in the system
    print(f'Amount of bots is set to {bot_num}')
    print('Initial bot states:')
    for i,j in bot_queue_dict.items():
        print(f'{i}: {j}')


    # ---- Thread Area ---- #

    #set_notification_event = threading.Thread(target=check_queue)

    # subscribe to the tasks send from the webserver (queue = 'rawTasksQueue')
    sub_webserver_task_queue_Thread = threading.Thread(target=sub_webserver_task_queue.subscribeToQueue, args=(from_webserver_task_callback,'rawTaskQueue'))

    # subscribe to the current location data from the bots (queues = 'currLoc.*)
    sub_botCurrLoc_Thread = threading.Thread(target=sub_bot_curr_loc.subscribeToTopic, args=(from_bot_callback,'bot_locs_topic','bot_locs','currLoc.*'))

    # publish a notification inside the queue 'notification' to the bots to notify them of new tasks
    # and trigger their publish method which sends their current location data
    pub_task_notification_Thread = threading.Thread(target=notify, args=(pub_task_notification, 'newTask'))

    # publishes the tasks for specific bots on their respective queue
    pub_bot_task_Thread = threading.Thread(target=publish_task, args=(pub_bot_task,))

    # publishes the coordinates of the chosen bot back to the webserver/client periodically
    # ...put here...

    # checks the queues periodically
    #debug_queue_Thread = threading.Thread(target=check_queue)

    # starts the threads

    sub_webserver_task_queue_Thread.start()
    sub_botCurrLoc_Thread.start()
    pub_task_notification_Thread.start()
    pub_bot_task_Thread.start()
    #debug_queue_Thread.start()

    # closes the threads gracefully

    sub_webserver_task_queue_Thread.join()
    sub_botCurrLoc_Thread.join()
    pub_task_notification_Thread.join()
    pub_bot_task_Thread.join()
    #debug_queue_Thread.join()


    # ---- Closing the RabbitMQ connections ---- #

    # closes the connection to RabbitMQ
    sub_webserver_task_queue.disconnect()
    sub_bot_curr_loc.disconnect()
    pub_task_notification.disconnect()
    pub_bot_task.disconnect()