from bot_class import Bot
import threading

if __name__ == "__main__":
    bot = Bot('192.168.56.106',5672,0,1)

    # Start a thread to listen for tasks
    brokerThread = threading.Thread(target=bot.start_listening_for_tasks)

    brokerThread.start()

    brokerThread.join()  # Wait for the listener thread to finish (it won't, unless interrupted)