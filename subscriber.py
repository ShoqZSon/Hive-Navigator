import pika
import pika.exceptions
import time


class Subscriber:
    def __init__(self, host:str, port:int):
        self.__host = host
        self.__port = port
        self.__connection = None
        self.__channel = None

    def connect(self) -> None:
        """Establish a connection to RabbitMQ."""
        while True:
            try:
                credentials = pika.credentials.PlainCredentials('administrator', 'admin')
                self.__connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.__host, port=self.__port, credentials=credentials)
                )
                self.__channel = self.__connection.channel()
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Connection failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def subscribe_to_queue(self,callback,queue:str) -> None:
        """Start consuming messages from a specific queue."""
        if self.__channel is None:
            raise Exception("Subscriber is not connected.")

        # ensures the queue exists before use.
        self.__channel.queue_declare(queue=queue,durable=True)

        self.__channel.basic_consume(queue=queue,
                                   on_message_callback=callback,
                                   auto_ack=True)

        print(f" [*] Waiting for messages in [{queue}]")

        self.__channel.start_consuming()

    def subscribe_to_topic(self, callback, exchange:str, queue:str, routing_key:str) -> None:
        """
        Bind a queue to a topic exchange to receive messages based on the routing key pattern.

        :parameter callback: the function to be executed when a message is received
        :parameter exchange: The name of the exchange to bind the queue to.
        :parameter routing_key: The routing key pattern to bind the queue with (e.g., 'key.*').
        :parameter queue: The name of the queue to bind to the exchange and receive messages.

        :return None
        """
        if self.__channel is None:
            raise Exception("Subscriber is not connected.")

        # Declare the topic exchange (must match the one used by the publisher).
        self.__channel.exchange_declare(exchange=exchange, exchange_type='topic')

        # Declare a queue (it can be the same queue for multiple routing keys)
        self.__channel.queue_declare(queue=queue, durable=True)

        # Bind the queue to the topic exchange with the specified routing key pattern.
        self.__channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

        print(f" [*] Queue [{queue}] is now bound to the topic exchange [{exchange}] with prefix [{routing_key}]")

        self.__channel.basic_consume(
            queue=queue,
            on_message_callback=callback,
            auto_ack=True
        )

        print(f" [*] Waiting for messages in topic exchange [{exchange}] with prefix {routing_key}")

        self.__channel.start_consuming()

    def subscribe_to_queue_tmp(self,callback,queue:str, timeout:int):
        """Start consuming messages from a specific queue."""
        if self.__channel is None:
            raise Exception("Subscriber is not connected.")

        # ensures the queue exists before use.
        self.__channel.queue_declare(queue=queue, durable=False,auto_delete=True)

        self.__channel.basic_consume(queue=queue,
                                     on_message_callback=callback,
                                     auto_ack=True)

        print(f" [*] Waiting for messages in [{queue}]")

        start_time = time.time()
        while True:
            # Check if the timeout period has elapsed
            if time.time() - start_time > timeout:
                print("Timeout reached. Stopping...")
                break

            # Process incoming messages
            self.__connection.process_data_events()
            time.sleep(1)  # Sleep to avoid busy-waiting

    def disconnect(self) -> None:
        """Close the connection to RabbitMQ."""
        if self.__connection:
            self.__connection.close()
            print(f'Connection: {self.__connection.channel} has been disconnected.')

