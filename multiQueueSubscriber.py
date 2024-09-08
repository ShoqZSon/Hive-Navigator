from subscriber import Subscriber


class MultiQueueSubscriber(Subscriber):
    def __init__(self,host,port):
        super().__init__(host,port)

