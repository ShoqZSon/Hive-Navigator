import pika


class Publisher:
    def __init__(self, host, port, exchange='', routing_key='defaultQueue'):
        self.host = host
        self.port = port
        self.exchange = exchange
        self.routing_key = routing_key
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

        self.channel.queue_declare(queue=self.routing_key)
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=self.routing_key,
                                   body=message)
        print(f" [x] Sent {message}")

    def close(self):
        """Close the connection to RabbitMQ."""
        if self.connection:
            self.connection.close()
            print("RabbitMQ connection is closed.")
