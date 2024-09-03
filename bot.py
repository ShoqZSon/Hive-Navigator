from publisher import Publisher
from subscriber import Subscriber
from bot_class import Bot
import threading
import sys
import queue

# queue for the tasks
task_queue = queue.Queue()

if __name__ == "__main__":
    #bot_id = sys.argv[1]
    #bot_hallNr = int(sys.argv[2])
    #bot_level = int(sys.argv[3])
    bot_id = 'bot1'
    bot_hallNr = 1
    bot_level = 0

    message_broker_host = '192.168.56.106'
    message_broker_port = 5672

    bot = Bot(bot_id,bot_hallNr,bot_level)


    # ---- Publisher & Subscriber Initialization ---- #

    # publisher for the bot data
    pub_bot_curr_loc = Publisher(message_broker_host, message_broker_port,exchange='topic_logs',routing_key=f'currLoc.{bot.getId()}')
    # subscriber to the notifications queue
    sub_task_notification = Subscriber(message_broker_host, message_broker_port, queue='',exchange='notification_exchange', exchange_type='fanout')    # subscriber for the bot tasks that listens on his own queue bot.{bot_id}
    #sub_bot_tasks = Subscriber(message_broker_host, message_broker_host,queue=f'tasks.{bot.getId()}')


    # ---- Connections to RabbitMQ ---- #

    # establishes the connection with the messageBroker
    pub_bot_curr_loc.connect()
    sub_task_notification.connect()
    #sub_bot_tasks.connect()


    # ---- Thread Area ---- #

    # publishes its data towards the messageBroker (=> towards the hivemind) on his own queue
    pub_bot_curr_loc_Thread = threading.Thread(target=bot.publishBotData,args=(pub_bot_curr_loc,f'currLoc.{bot.getId()}'))
    sub_task_notification_Thread = threading.Thread(target=sub_task_notification.startConsuming,args=(bot.notificationCallback,))
    #sub_bot_tasks_Thread = threading.Thread(target=sub_botCurrLoc.start_consuming, args=(bot.addTask,))

    # starts the threads
    pub_bot_curr_loc_Thread.start()
    sub_task_notification_Thread.start()
    #sub_bot_tasks_Thread.start()

    # closes the threads gracefully
    pub_bot_curr_loc_Thread.join()
    sub_task_notification_Thread.join()
    #sub_botTasks_Thread.join()


    # ---- Closing the RabbitMQ connections ---- #

    # closes the connection to RabbitMQ
    pub_bot_curr_loc.close()
    sub_task_notification.close()
    #sub_bot_tasks.close()
