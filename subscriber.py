import pika
import pika.exceptions
import time


class Subscriber:
    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None
        self.subscriptions = []

    def connect(self) -> None:
        """Establish a connection to RabbitMQ."""
        while True:
            try:
                credentials = pika.credentials.PlainCredentials('administrator', 'admin')
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
                )
                self.channel = self.connection.channel()
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Connection failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def subscribe_to_queue(self,callback,queue:str) -> None:
        """Start consuming messages from a specific queue."""
        if self.channel is None:
            raise Exception("Subscriber is not connected.")

        # ensures the queue exists before use.
        self.channel.queue_declare(queue=queue,durable=True)

        self.channel.basic_consume(queue=queue,
                                   on_message_callback=callback,
                                   auto_ack=True)

        print(f" [*] Waiting for messages in [{queue}]")

        self.channel.start_consuming()

    def subscribe_to_topic(self, callback, exchange:str, queue:str, routing_key:str) -> None:
        """
        Bind a queue to a topic exchange to receive messages based on the routing key pattern.

        :parameter callback: the function to be executed when a message is received
        :parameter exchange: The name of the exchange to bind the queue to.
        :parameter routing_key: The routing key pattern to bind the queue with (e.g., 'key.*').
        :parameter queue: The name of the queue to bind to the exchange and receive messages.

        :return None
        """
        if self.channel is None:
            raise Exception("Subscriber is not connected.")

        # Declare the topic exchange (must match the one used by the publisher).
        self.channel.exchange_declare(exchange=exchange, exchange_type='topic')

        # Declare a queue (it can be the same queue for multiple routing keys)
        self.channel.queue_declare(queue=queue, durable=True)

        # Bind the queue to the topic exchange with the specified routing key pattern.
        self.channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

        print(f" [*] Queue [{queue}] is now bound to the topic exchange [{exchange}] with prefix [{routing_key}]")

        self.channel.basic_consume(
            queue=queue,
            on_message_callback=callback,
            auto_ack=True
        )

        print(f" [*] Waiting for messages in topic exchange [{exchange}] with prefix {routing_key}")

        self.channel.start_consuming()

    def close(self) -> None:
        """Close the connection to RabbitMQ."""
        print("killing connection")
        if self.connection:
            self.connection.close()

    def getSubscriptions(self) -> list:
        return self.subscriptions
