class Subscriber:
    _id = 0
    def __init__(self):
        # holds subscription objects to publishers
        self.subscriptions = []
        # creates a unique id for every subscriber instance
        self.id = Subscriber._id
        Subscriber._id += 1

    def subscribeTo(self,publisher):
        if publisher not in self.subscriptions:
            self.subscriptions.append(publisher)
            print(f"Subscriber {self.id} subscribed to {publisher.id}")
            publisher.addSub(self)

    def unsubscribeFrom(self,publisher):
        if publisher in self.subscriptions:
            self.subscriptions.remove(publisher)
            print(f"Subscriber {self.id} removed subscription from {publisher.id}")
            publisher.removeSub(self)

    def notificationFromPub(self, topic, message, publisher):
        print(f"Receveived update from {publisher.id}: {topic} - {message}")

    def subscriber_info(self):
        print("I am a subscriber")
