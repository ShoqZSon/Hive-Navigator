class Publisher:
    _id = 0
    def __init__(self):
        # holds the subscribers of this publisher instance
        self.subscribers = []
        # creates a unique id for every publisher instance
        self.id = Publisher._id
        Publisher._id += 1

    def publish(self):
        pass

    def addSub(self, subscriber) -> None:
        """
        Adds a subscriber to the list of subscribers

        :param subscriber: the subscriber to add
        :return: None
        """
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)
            print(f"Added subscriber: {subscriber.id}")

    def removeSub(self, subscriber) -> None:
        """
        Remove subscriber from the list of subscribers

        :param subscriber: the subscriber to remove
        :return: None
        """
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)
            print("Removed subscriber: {subscriber.id}")

    def notifySubs(self, topic, message) -> None:
        """
        Notifies every subscriber of some update

        :param topic: the topic of the notification
        :param message: contains some message
        :return: None
        """
        for subscriber in self.subscribers:
            print(f"Notifying subscriber: {subscriber.id}")
            subscriber.notificationFromPub(topic,message, self)

    def publisher_info(self):
        print("I am a publisher")