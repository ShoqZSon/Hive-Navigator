from publisher import Publisher

class MultiQueuePublisher(Publisher):
    def __init__(self, messageBrokerHost, messageBrokerPort, queue_prefix='currLoc_', exchange='topic_logs'):
        super().__init__(messageBrokerHost, messageBrokerPort, exchange)
        self.queue_prefix = queue_prefix

    def publish_to_all(self, message, suffixes):
        """Publish messages to all queues with the given suffixes."""
        if self.channel is None:
            raise Exception("Publisher is not connected.")

        for suffix in suffixes:
            routing_key = f'{self.queue_prefix}{suffix}'
            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=routing_key,
                                       body=message)
            print(f" [x] Sent {message} to {routing_key}")