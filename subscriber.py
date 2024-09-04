import pika


class Subscriber:
    def __init__(self, host, port, queue=''):
        self.host = host
        self.port = port
        self.queue = queue
        self.connection = None
        self.channel = None
        self.subscriptions = []

    def connect(self):
        """Establish a connection to RabbitMQ."""
        credentials = pika.credentials.PlainCredentials('administrator', 'admin')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port,credentials=credentials))
        self.channel = self.connection.channel()

    def subscribe_to_queue(self,callback):
        """Start consuming messages from the queue."""
        if self.channel is None:
            raise Exception("Subscriber is not connected.")

        # ensures the queue exists before use.
        self.channel.queue_declare(queue=self.queue,durable=True)

        self.channel.basic_consume(queue=self.queue,
                                   on_message_callback=callback,
                                   auto_ack=True)

        print(f" [*] Waiting for messages in {self.queue}")

    def startConsuming(self, callback):
        self.subscribe_to_queue(callback)
        self.channel.start_consuming()

    def close(self):
        """Close the connection to RabbitMQ."""
        if self.connection:
            self.connection.close()

    def getSubscriptions(self):
        return self.subscriptions
