import pika


class Subscriber:
    def __init__(self, host, port, queue='defaultQueue',exchange='',exchange_type=''):
        self.host = host
        self.port = port
        self.queue = queue
        # holds the connection object (rabbitmq object)
        self.connection = None
        self.channel = None
        self.subscriptions = []
        self.exchange = exchange
        self.exchange_type = exchange_type

    def connect(self):
        """Establish a connection to RabbitMQ."""
        credentials = pika.credentials.PlainCredentials('administrator', 'admin')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port,credentials=credentials))
        self.channel = self.connection.channel()
        if self.exchange:
            self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type, durable=True)

        # Declare queue
        self.channel.queue_declare(queue=self.queue, durable=True)

        # Bind queue to exchange if exchange is specified
        if self.exchange:
            self.channel.queue_bind(exchange=self.exchange, queue=self.queue)

    def startConsuming(self, callback):
        """Start consuming messages from the queue."""
        if self.channel is None:
            raise Exception("Subscriber is not connected.")

        # Method: is used to set up a consumer on a RabbitMQ queue
        # queue: Specifies the name of the queue from which messages will be consumed.
        # on_message_callback: Defines the function that will be called whenever a new message arrives in the specified queue.
        # auto_ack: ensures that RabbitMQ gets a response back to pop the item from the queue
        self.channel.basic_consume(queue=self.queue,
                                   on_message_callback=callback,
                                   auto_ack=True)

        print(f" [*] Waiting for messages in {self.queue}. To exit press CTRL+C")
        # Starts an infinite loop that waits for the messages to arrive and calls the callback function to process them
        self.channel.start_consuming()

    def close(self):
        """Close the connection to RabbitMQ."""
        if self.connection:
            self.connection.close()

    def getSubscriptions(self):
        return self.subscriptions
