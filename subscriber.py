class Subscriber:
    _id = 0

    def __init__(self):
        """
        Initializes a new Subscriber instance.

        Creates a unique ID for the subscriber and initializes an empty list
        to hold the subscriptions to publishers.
        """
        self.subscriptions = []
        self.id = Subscriber._id
        Subscriber._id += 1

    def subscribeTo(self, publisher) -> None:
        """
        Subscribes the subscriber to a given publisher.

        If the subscriber is not already subscribed to the publisher, this method
        adds the publisher to the subscriber's subscription list and adds the
        subscriber to the publisher's list of subscribers.

        :param publisher: The publisher to subscribe to.
        :return: None
        """
        if publisher not in self.subscriptions:
            self.subscriptions.append(publisher)
            print(f"Subscriber {self.id} subscribed to {publisher.id}")
            publisher.addSub(self)

    def unsubscribeFrom(self, publisher) -> None:
        """
        Unsubscribes the subscriber from a given publisher.

        If the subscriber is currently subscribed to the publisher, this method
        removes the publisher from the subscriber's subscription list and removes
        the subscriber from the publisher's list of subscribers.

        :param publisher: The publisher to unsubscribe from.
        :return: None
        """
        if publisher in self.subscriptions:
            self.subscriptions.remove(publisher)
            print(f"Subscriber {self.id} removed subscription from {publisher.id}")
            publisher.removeSub(self)

    def notificationFromPub(self, topic:str, message, publisher) -> None:
        """
        Receives a notification from a publisher.

        This method is called by a publisher when it sends out a notification. It
        prints out the received update, including the publisher's ID, the topic,
        and the message.

        :param topic: The topic of the notification.
        :param message: The message content of the notification.
        :param publisher: The publisher that sent the notification.
        :return: None
        """
        print(f"Received update from {publisher.id}: {topic} - {message}")

    def subscriber_info(self) -> None:
        """
        Prints basic information about the subscriber.

        This method provides a simple output indicating that this instance is a subscriber.

        :return: None
        """
        print("I am a subscriber")
