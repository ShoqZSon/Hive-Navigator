from subscriber import Subscriber


class MultiQueueSubscriber(Subscriber):
    def __init__(self,host,port,exchange='', routing_key='',queue=''):
        super().__init__(host,port,queue)
        self.exchange = exchange
        self.routing_key = routing_key

    def subscribe_to_topic(self,callback):
        """
        Bind multiple queues to a topic exchange to receive messages based on the routing key pattern.
        """
        if self.channel is None:
            raise Exception("Subscriber is not connected.")

        # Declare the topic exchange (must match the one used by the publisher).
        self.channel.exchange_declare(exchange=self.exchange, exchange_type='topic')

        # Declare a queue (it can be the same queue for multiple routing keys)
        self.channel.queue_declare(queue=self.queue, durable=True)

        # Bind the queue to the topic exchange with the specified routing key pattern.
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)

        print(f" [*] Queue {self.queue} is now bound to the topic exchange {self.exchange} with prefix {self.routing_key}")

        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=callback,
            auto_ack=True
        )

    def startConsuming(self, callback):
        self.subscribe_to_topic(callback)
        self.channel.start_consuming()
