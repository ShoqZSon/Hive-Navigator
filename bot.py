import publisher as p
import subscriber as s

"""
"""
class Bot(p.Publisher,s.Subscriber):
    """The Bot class is run on the bots themselves. It receives the best fitting task in terms of the distance between itself and the location of the customers.
    It then proceeds to drive towards them while calculating the most efficient route.
    The Bot class is derived by the Publisher and Subscriber class in order to Publish its own coordinates towards the hivemind for comparison and Subscribe to the hivemind for the tasks.
    """
    def __init__(self):
        """Receives the parameters of Publisher and Subscriber:
            Publisher:
                Array of subscribers -> subscribers = []
            Subscriber:


        """
        super().__init__()