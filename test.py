import publisher as pub
import subscriber as sub
import json

if __name__ == '__main__':
    queue = []

    pub1 = pub.Publisher()
    pub2 = pub.Publisher()

    sub1 = sub.Subscriber()
    sub2 = sub.Subscriber()
    sub3 = sub.Subscriber()
    sub4 = sub.Subscriber()

    sub1.subscribeTo(pub1)

    # Create a dictionary with location and destination
    data = {
        "location": "loc2",
        "destination": "205,1,0,15,20"
    }

    # Convert the dictionary to a JSON string
    message = json.dumps(data)

    pub1.notifySubs("New Task", message)

    # Create a dictionary with location and destination
    data = {
        "location": "loc1",
        "destination": "1,2,3,4,5"
    }

    # Convert the dictionary to a JSON string
    message = json.dumps(data)

    pub1.notifySubs("New Task", message)