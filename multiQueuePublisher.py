from publisher import Publisher


class MultiQueuePublisher(Publisher):
    def __init__(self, messageBrokerHost, messageBrokerPort, exchange='',routing_key='',queue=''):
        super().__init__(messageBrokerHost, messageBrokerPort, exchange,queue)
        self.routing_key = routing_key

    def publish(self, message):
        """
        Publish a message to all queues bound to a fanout exchange.
        """
        if self.channel is None:
            raise Exception("Publisher is not connected.")

        # Declare a fanout exchange. This exchange will broadcast messages to all bound queues.
        self.channel.exchange_declare(exchange=self.exchange, exchange_type='topic')

        # Publish the message to the fanout exchange.
        # Since it's a fanout exchange, the routing key is ignored.
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=message
        )
        print(f" [x] Sent {self.routing_key}:{message}")