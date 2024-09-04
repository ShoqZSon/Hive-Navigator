import pika
import pika.exceptions
import time


class Publisher:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish a connection to RabbitMQ."""
        while True:
            try:
                credentials = pika.credentials.PlainCredentials('administrator', 'admin')
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host, port=self.port,credentials=credentials)
                )
                self.channel = self.connection.channel()
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Connection failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def publish_to_queue(self, message, queue):
        """Publish a message to the specified queue."""
        try:
            if self.channel is None:
                raise Exception("Publisher is not connected.")

            # ensures the queue exists before use.
            self.channel.queue_declare(queue=queue, durable=True)

            self.channel.basic_publish(exchange='',
                                       routing_key=queue,
                                       body=message)

            print(f" [x] Sent {message} to {queue}")
        except (pika.exceptions.StreamLostError,pika.exceptions.AMQPChannelError) as e:
            print(f"Publishing error: {e}. Reconnecting...")
            self.connect()  # Reconnect
            self.publish_to_queue(message, queue)  # Retry publishing
        except Exception as e:
            print(f"Unexpected error during publishing: {e}")

    def publish_to_topic(self, message, exchange, routing_key):
        """Publish a message to all queues bound to a fanout exchange."""
        try:
            if self.channel is None:
                raise Exception("Publisher is not connected.")

            # Declare a fanout exchange. This exchange will broadcast messages to all bound queues.
            self.channel.exchange_declare(exchange=exchange, exchange_type='topic')

            # Publish the message to the fanout exchange.
            # Since it's a fanout exchange, the routing key is ignored.
            self.channel.basic_publish(
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

    def close(self):
        """Close the connection to RabbitMQ."""
        if self.connection:
            self.connection.close()
            print("RabbitMQ connection is closed.")
