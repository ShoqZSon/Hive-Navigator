import pika


class Publisher:
    def __init__(self, host, port, exchange='', routing_key='defaultQueue'):
        self.host = host
        self.port = port
        self.exchange = exchange
        self.routing_key = routing_key
        # holds the connection object (rabbitmq object)
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish a connection to RabbitMQ."""
        credentials = pika.credentials.PlainCredentials('administrator', 'admin')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port,credentials=credentials))
        self.channel = self.connection.channel()

    def publish(self, message,queue):
        """Publish a message to the specified queue."""
        if self.channel is None:
            raise Exception("Publisher is not connected.")

        # ensures the queue exists before use.
        self.channel.queue_declare(queue=queue, durable=True)

        # Method: publish a message to RabbitMQ
        # exchange: Specifies the name of the exchange to which the message will be published.
        # routing_key: Determines the routing of the message within the exchange.
        # body: Specifies the content of the message being sent.
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=queue,
                                   body=message)
        print(f" [x] Sent {message} to {queue}")

    def close(self):
        """Close the connection to RabbitMQ."""
        if self.connection:
            self.connection.close()
            print("RabbitMQ connection is closed.")
