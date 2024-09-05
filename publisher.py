import pika
import pika.exceptions
import time


class Publisher:
    def __init__(self, host, port):
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
                    pika.ConnectionParameters(host=self.__host, port=self.__port,credentials=credentials)
                )
                self.__channel = self.__connection.channel()
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Connection failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def publish_to_queue(self, message, queue:str,auto_delete=False,durable=True) -> None:
        """Publish a message to the specified queue."""
        try:
            if self.__channel is None:
                raise Exception("Publisher is not connected.")

            # ensures the queue exists before use.
            self.__channel.queue_declare(queue=queue, durable=durable,auto_delete=auto_delete)

            self.__channel.basic_publish(exchange='',
                                       routing_key=queue,
                                       body=message)

            print(f" [x] Sent {message} to {queue}")
        except (pika.exceptions.StreamLostError,pika.exceptions.AMQPChannelError) as e:
            print(f"Publishing error: {e}. Reconnecting...")
            self.connect()  # Reconnect
            self.publish_to_queue(message, queue)  # Retry publishing
        except Exception as e:
            print(f"Unexpected error during publishing: {e}")

    def publish_to_topic(self, message, exchange:str, routing_key:str) -> None :
        """Publish a message to all queues bound to a fanout exchange."""
        try:
            if self.__channel is None:
                raise Exception("Publisher is not connected.")

            # Declare a fanout exchange. This exchange will broadcast messages to all bound queues.
            self.__channel.exchange_declare(exchange=exchange, exchange_type='topic')

            # Publish the message to the fanout exchange.
            # Since it's a fanout exchange, the routing key is ignored.
            self.__channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message
            )

            print(f" [x] Sent '{message}' to exchange '{exchange}' with routing key '{routing_key}'")
        except (pika.exceptions.StreamLostError,pika.exceptions.AMQPChannelError) as e:
            print(f"Publishing error: {e}. Reconnecting...")
            self.connect()  # Reconnect
            self.publish_to_topic(message, exchange, routing_key)  # Retry publishing
        except Exception as e:
            print(f"Unexpected error during publishing: {e}")

    def disconnect(self) -> None:
        """Close the connection to RabbitMQ."""
        if self.__connection:
            self.__connection.close()
            print(f'Connection: {self.__connection.channel} has been disconnected.')
