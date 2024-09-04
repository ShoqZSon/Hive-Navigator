import pika


class Publisher:
    def __init__(self, host, port, exchange='', routing_key='', queue=''):
        self.host = host
        self.port = port
        self.exchange = exchange
        self.routing_key = routing_key
        self.queue = queue
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish a connection to RabbitMQ."""
        credentials = pika.credentials.PlainCredentials('administrator', 'admin')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port,credentials=credentials))
        self.channel = self.connection.channel()

    def publish(self, message):
        """Publish a message to the specified queue."""
        if self.channel is None:
            raise Exception("Publisher is not connected.")

        # ensures the queue exists before use.
        self.channel.queue_declare(queue=self.queue, durable=True)

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=self.queue,
                                   body=message)
        print(f" [x] Sent {message} to {self.queue}")

    def close(self):
        """Close the connection to RabbitMQ."""
        if self.connection:
            self.connection.close()
            print("RabbitMQ connection is closed.")
