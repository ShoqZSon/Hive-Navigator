from flask import Flask, render_template, request, redirect, url_for
import json
import sys
from publisher import Publisher
from subscriber import Subscriber


app = Flask(__name__)

def showBotCoordinates(ch,method,properties,body):
    print(f'{body}')

def extractData(data:str,separator:str) -> str:
    """
    Extracts the important data from the string comma-based.
    :param data: string of comma-separated data.
    :param separator: the separator to separate the string into list entries.

    :return: str of comma-separated data.
    """
    # TODO: location will need this as well
    tmp = data.split(separator)
    # TODO: Probably needs adaption since hard coding the elements to remove is inflexible
    tmp.pop(0)
    tmp.pop(3)
    data = separator.join(tmp)

    return data

def prepData(location:str, destination:str) -> str:
    """
    Prepares the data from the raw strings location and destination to a json data object.
    :param location: str
            location of the terminal the customer sent the task from
    :param destination: str
            desired destination of the customer

    Format of the data:
            data = {
                "location": str,
                "destination": str
            }

    :return: str of data
    """
    # Create a dictionary with location and destination
    data = {
        "location": location,
        "destination": destination
    }

    # Convert the dictionary to a JSON string
    message = json.dumps(data)

    return message

def sendDataToRabbitMQ(message, host:str, port:int,queue='rawTaskQueue') -> None:
    """
    Sends a message to the message broker RabbitMQ.
    :param message: The data to be sent
    :param host: The host of the RabbitMQ server
    :param port: The port of the RabbitMQ server
    :param queue: The queue to send messages to (defaults to 'rawTaskQueue')
    """
    pub_webserver_task_queue = Publisher(host=host, port=port)
    pub_webserver_task_queue.connect()
    pub_webserver_task_queue.publish_to_queue(message,queue=queue)
    pub_webserver_task_queue.disconnect()

def receiveBotData(host:str, port:int,queue='botTaskQueue'):
    """
    Receives the bot data (coordinates) periodically to display on a map on the page followBot.html.

    :param host:
    :param port:
    :param queue:
    """
    sub_bot_data = Subscriber(host=host, port=port)
    sub_bot_data.connect()
    sub_bot_data.subscribe_to_queue(callback=showBotCoordinates, queue=queue)
    sub_bot_data.disconnect()

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """/submit route is supposed to receive the data from index.html and sends it further

    This route receives the data (location of the terminal and the destination of the customer).
    1. The Hall-Nr, Floor, x and y coordinate get extracted from the dictionaries with extractData().
    2. The extracted data gets transformed to a json object => prepared for sending properly.
    3. The json data gets sent to the message broker on given host, port and into the rawTaskQueue.

    Arguments
    ---------
    -

    Important Variables
    -------------------
        location: right now -> string with one entry
            location represents the coordinates of the terminal
        destination: Stand-Name, Stand-Nr, Hallen-Nr, Ebene, Thema, x-coordinate, y-coordinate
            After trimming -> Stand-Nr, Hallen-Nr, Ebene, x-coordinate, y-coordinate

    It is possible to just keep sending tasks into the queue without anyone using them.
    This will just stack the tasks.
    """
    location = request.form.get('location')
    destination = request.form.get('destination')

    # Process the form data here
    print(f"Location: {location}")
    print(f"Destination: {destination}")

    # Removes the Stand-Name and the Thema because the robot does not need it
    # location = sD.extractData(location)
    destination = extractData(destination,",")

    # prepares the data for sending
    dataToSend = prepData(location, destination)
    # append new task to the rawTaskQueue
    sendDataToRabbitMQ(dataToSend,'192.168.56.106',5672,'rawTaskQueue')

    return redirect(url_for('success'))

@app.route('/success')
def success():
    """The /success route gets called when the task has been successfully transmitted
    It then proceeds to show the customer a map and an ETA of the robot towards their location
    """
    # TODO: Success page is supposed to show the current position of the bot + ETA
    #receiveBotData('192.168.56.106',5672,'botTaskQueue')
    return render_template('followBot.html')

if __name__ == '__main__':
    # webserverHost = sys.argv[1]
    # webserverPort = int(sys.argv[2])

    # if not webserverHost or not webserverPort:
    #    print(f"{webserverHost}:{webserverPort} is not set")
    #    exit(-1)

    app.run(host='localhost', port=5000, debug=True)
