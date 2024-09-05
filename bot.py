from publisher import Publisher
from subscriber import Subscriber
from bot_class import Bot
import threading
import sys
import queue

# queue for the tasks
task_queue = queue.Queue()

if __name__ == "__main__":
    bot_id = sys.argv[1]
    #bot_hallNr = int(sys.argv[2])
    #bot_level = int(sys.argv[3])
    #bot_id = 'bot2'
    bot_hallNr = 1
    bot_level = 0

    message_broker_host = '192.168.56.106'
    message_broker_port = 5672

    bot = Bot(bot_id,bot_hallNr,bot_level)

    # ---- Publisher & Subscriber Initialization ---- #

    pub_one_time_notification = Publisher(message_broker_host,message_broker_port)

    # publisher for the bot data
    pub_bot_curr_loc = Publisher(message_broker_host, message_broker_port)
    # subscriber to the notifications queue
    sub_task_notification = Subscriber(message_broker_host, message_broker_port)
    # subscriber for the bot tasks that listens on his own queue bot.{bot_id}
    sub_bot_tasks = Subscriber(message_broker_host, message_broker_port)


    # ---- Connections to RabbitMQ ---- #

    # establishes the connection with the messageBroker
    pub_one_time_notification.connect()
    pub_bot_curr_loc.connect()
    sub_task_notification.connect()
    #sub_bot_tasks.connect()

    pub_one_time_notification.publish_to_queue(bot.getId(),'initial_existence_share',auto_delete=True,durable=False)
    pub_one_time_notification.disconnect()


    # ---- Thread Area ---- #

    # publishes the bot data towards the hivemind for processing waits until a notification from the hivemind gets sent
    pub_bot_curr_loc_Thread = threading.Thread(target=bot.publishBotData,args=(pub_bot_curr_loc,))
    # subscribes the notification queue in order to let the bot know when to publish its data
    sub_task_notification_Thread = threading.Thread(target=sub_task_notification.subscribe_to_topic,args=(bot.notificationCallback,'notification_topic',f'notifications_{bot.getId()}','notification.*'))
    #sub_bot_tasks_Thread = threading.Thread(target=sub_bot_tasks.subscribe_to_queue, args=(bot.addTask_callback,f'tasks.{bot.getId()}'))

    # starts the threads
    pub_bot_curr_loc_Thread.start()
    sub_task_notification_Thread.start()
    #sub_bot_tasks_Thread.start()

    # closes the threads gracefully
    pub_bot_curr_loc_Thread.join()
    sub_task_notification_Thread.join()
    #sub_bot_tasks_Thread.join()


    # ---- Closing the RabbitMQ connections ---- #

    # closes the connection to RabbitMQ
    pub_bot_curr_loc.disconnect()
    sub_task_notification.disconnect()
    #sub_bot_tasks.disconnect()
