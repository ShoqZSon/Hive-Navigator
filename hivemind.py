from hivemind_class import Hivemind
import threading


hivemind = Hivemind('192.168.56.106',5672,'192.168.56.102',57920)

webserverThread = threading.Thread(target=hivemind.listenToConn())
# hivemind listens to incoming coordinates from the bots
brokerThread = threading.Thread(target=hivemind.start_listening_for_locations())

brokerThread.start()
webserverThread.start()

brokerThread.join()
webserverThread.join()

hivemind.close()