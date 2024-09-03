from multiQueuePublisher import MultiQueuePublisher
from subscriber import Subscriber
from multiQueueSubscriber import MultiQueueSubscriber
import json
import threading
import queue

task_queue = queue.Queue()

newTask_Event = threading.Event()

def decode_json_object(jsonObject) -> dict:
    task_str = jsonObject.decode('utf-8')
    task = json.loads(task_str)

    return task

def task_callback(ch, method, properties, body):
    """Used to handle the rawTaskQueue items"""
    print("task_callback")
    task = decode_json_object(body)
    print(f"Received {task}")

    # Enqueue the task for publishing
    task_queue.put(task)

    newTask_Event.set()

def loc_callback(ch, method, properties, body):
    """Used to handle the botCurrLoc.* items"""
    print("loc_callback")

    task = decode_json_object(body)
    print(f"Received {task}")

def publish_task(publisher,botCurrLoc,botQueue):
    """Publishes messages from the queue as they become available."""
    newTask_Event.wait()
    print("done waiting")
    while True:
        task = task_queue.get()  # Wait for a task to be available in the queue
        if task is None:
            break  # Exit the loop if None is received (for shutdown)

        selected_task = compare_userLoc_botLoc(task,botCurrLoc)
        publisher.publish(selected_task, queue=botQueue)
        print(f"Published task {selected_task}")
        task_queue.task_done()
        newTask_Event.clear()

def compare_userLoc_botLoc(usrLoc, botCurrLoc) -> dict:
    print("Comparing userLoc and botLoc")
    print(f"usrLoc: {usrLoc}")
    print(f"botLoc: {botCurrLoc.getSubscriptions()}")

    return {}


if __name__ == '__main__':
    messageBrokerHost = '192.168.56.106'
    messageBrokerPort = 5672

    # listens to the tasks coming from the webserver
    sub_webserverTaskQueue = Subscriber(messageBrokerHost, messageBrokerPort,'rawTaskQueue')
    # listens to the coordinates(x,y), hall-nr, level of any bot that publishes to any queue "currLoc_*"
    sub_botCurrLoc = MultiQueueSubscriber(messageBrokerHost, messageBrokerPort,queue_prefix='currLoc',exchange='topic_logs')
    # publishes back to the corresponding bots with their respective task
    pub_botTasks = MultiQueuePublisher(messageBrokerHost, messageBrokerPort,queue_prefix='tasks',exchange='topic_logs')

    sub_webserverTaskQueue.connect()
    sub_botCurrLoc.connect()
    pub_botTasks.connect()

    sub_webserverTaskQueue_Thread = threading.Thread(target=sub_webserverTaskQueue.start_consuming, args=(task_callback,))
    sub_botCurrLoc_Thread = threading.Thread(target=sub_botCurrLoc.start_consuming, args=(loc_callback,))
    pub_botTasks_Thread = threading.Thread(target=publish_task, args=(pub_botTasks,sub_botCurrLoc,'currLoc.'))

    sub_webserverTaskQueue_Thread.start()
    sub_botCurrLoc_Thread.start()
    pub_botTasks_Thread.start()

    sub_webserverTaskQueue_Thread.join()
    sub_botCurrLoc_Thread.join()
    pub_botTasks_Thread.join()

    sub_webserverTaskQueue.close()
    sub_botCurrLoc.close()
    pub_botTasks.close()