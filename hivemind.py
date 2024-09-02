from hivemind_class import Hivemind
import threading


hivemind = Hivemind('192.168.56.106',5672,'192.168.56.102',57920)

webserverThread = threading.Thread(target=hivemind.listen_to_conn())
listeningToIncomingLocationsThread = threading.Thread(target=hivemind.start_listening_for_locations())

webserverThread.start()
listeningToIncomingLocationsThread.start()

webserverThread.join()
listeningToIncomingLocationsThread.join()


hivemind.close()