import json


class Hivemind:
    """The Hivemind class acts as middleman between the webserver and the bots. It is supposed to receive the tasks, store them in a queue and distribute them to the best fitting bot.
    Best fitting is determined through a comparison between the destination coordinates and the current coordinates of the bot. The closest is the best fitting.
    Hivemind is derived from Publisher and Subscriber since it needs to Publish its own queue towards the bots and Subscribe to the bots to receive the coordinates.

    Attributes
    ----------
    queue: list
        a queue of tasks (location and destination)

    Methods
    -------
    listenToConn()
        starts the listening-server towards the client (webserver)
    """
    def __init__(self):
        pass

