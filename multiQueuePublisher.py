from publisher import Publisher


class MultiQueuePublisher(Publisher):
    def __init__(self, messageBrokerHost, messageBrokerPort, exchange='',routing_key='',queue=''):
        super().__init__(messageBrokerHost, messageBrokerPort, exchange,queue)
        self.routing_key = routing_key

