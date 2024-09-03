from publisher import Publisher
from subscriber import Subscriber
from bot_class import Bot
import threading
import sys
import queue


task_queue = queue.Queue()




if __name__ == "__main__":
    #bot_id = sys.argv[1]
    #bot_hallNr = int(sys.argv[2])
    #bot_level = int(sys.argv[3])
    bot_id = 'bot1'
    bot_hallNr = 1
    bot_level = 0

    messageBrokerHost = '192.168.56.106'
    messageBrokerPort = 5672

    bot = Bot(bot_id,bot_hallNr,bot_level)

    pub_botCurrLoc = Publisher(messageBrokerHost, messageBrokerPort,exchange='topic_logs',routing_key=f'currLoc.{bot.getId()}')
    sub_botCurrLoc = Subscriber(messageBrokerHost, messageBrokerPort,queue=f'tasks.{bot.getId()}')

    pub_botCurrLoc.connect()
    sub_botCurrLoc.connect()

    sub_botCurrLoc_Thread = threading.Thread(target=sub_botCurrLoc.start_consuming, args=(bot.addTask,))
    botExecuteTask_Thread = threading.Thread(target=bot.executeTask)
    pub_botCurrLoc_Thread = threading.Thread(target=bot.publish_botData,args=(pub_botCurrLoc,f'currLoc.{bot.getId()}',))

    sub_botCurrLoc_Thread.start()
    botExecuteTask_Thread.start()
    pub_botCurrLoc_Thread.start()

    sub_botCurrLoc_Thread.join()
    botExecuteTask_Thread.join()
    pub_botCurrLoc_Thread.join()

    sub_botCurrLoc.close()
    pub_botCurrLoc.close()
