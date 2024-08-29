import publisher as p
import subscriber as s
import threading
import time
import json
import socket

class Bot(p.Publisher,s.Subscriber):
    """The Bot class is run on the bots themselves. It receives the best fitting task in terms of the distance between itself and the location of the customers.
    It then proceeds to drive towards them while calculating the most efficient route.
    The Bot class is derived by the Publisher and Subscriber class in order to Publish its own coordinates towards the hivemind for comparison and Subscribe to the hivemind for the tasks.
    """
    bot_id = 0
    def __init__(self,hivemind_host='127.0.0.1',hivemind_port=65432):
        """Receives the parameters of Publisher and Subscriber:
            Publisher:
                Array of subscribers -> subscribers = []
            Subscriber:


        """
        super().__init__()
