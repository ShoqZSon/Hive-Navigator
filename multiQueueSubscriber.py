from subscriber import Subscriber


class MultiQueueSubscriber(Subscriber):
    def __init__(self,host,port,queue_prefix='currLoc_',exchange='topic_logs'):
        super().__init__(host,port)
        self.queue_prefix = queue_prefix
        self.exchange = exchange

    def connect(self):
        super().connect()
        self.declareTopicExchange()
        self.bindQueue()

    def declareTopicExchange(self):
        self.channel.exchange_declare(exchange=self.exchange,exchange_type='topic')

    def bindQueue(self):
        print("Looking for any new binds")
        queue = f'{self.queue_prefix}.*'
        routing_key = f'{self.queue_prefix}.*'
        if queue not in self.subscriptions:
            print(f"Found new bind {queue}")
            # Declare the queue
            self.channel.queue_declare(queue=queue, durable=True)

            # Bind the queue to the exchange with the routing key
            self.channel.queue_bind(exchange=self.exchange, queue=queue, routing_key=routing_key)

            # Keep track of the queues bound
            self.subscriptions.append(queue)

    def startConsuming(self, callback):
        """Start consuming messages from all bound queues."""
        if self.channel is None:
            raise Exception("Subscriber is not connected.")

        for queue in self.subscriptions:
            self.channel.basic_consume(queue=queue,
                                       on_message_callback=callback,
                                       auto_ack=True)

        print(f" [*] Waiting for messages in {', '.join(self.subscriptions)}. To exit press CTRL+C")
        self.channel.start_consuming()
