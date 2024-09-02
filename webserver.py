from flask import Flask, render_template, request, redirect, url_for
import json
import socket
import sys
from publisher import Publisher


app = Flask(__name__)

def extractData(data:str,separator:str) -> str:
    """
    Extracts the important data from the string commabased.
    :param data: string of comma-separated data.
    :param separator: the separator to separate the string into list entries.

    :return: str
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

    :return: str
    """
    # Create a dictionary with location and destination
    data = {
        "location": location,
        "destination": destination
    }

    # Convert the dictionary to a JSON string
    message = json.dumps(data)

    return message

def sendDataToRabbitMQ(message, host:str, port:int) -> None:
    pub = Publisher(host=host, port=port,routing_key='rawTaskQueue')
    pub.connect()
    pub.publish(message,'rawTaskQueue')
    pub.close()


@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """/submit route is supposed to receive the data from index.html and sends it further

    This route receives the data (location and destination of the customer).
    Another sendData method is called which sends the data to the given host and port.

    Arguments
    ---------
    -

    Important Variables
    -------------------
        location: right now -> string with one entry
        destination: Stand-Name, Stand-Nr, Hallen-Nr, Ebene, Thema, x-coordinate, y-coordinate
            After trimming -> Stand-Nr, Hallen-Nr, Ebene, x-coordinate, y-coordinate

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

    # send the data to rabbitMQ
    sendDataToRabbitMQ(dataToSend,'192.168.56.106',5672)

    return redirect(url_for('success'))

@app.route('/success')
def success():
    """The /success route gets called when the task has been successfully transmitted
    It then proceeds to show the customer a map and an ETA of the robot towards their location
    """
    # TODO: Success page is supposed to show the current position of the bot + ETA

    return render_template('followBot.html')

if __name__ == '__main__':
    # webserverHost = sys.argv[1]
    # webserverPort = int(sys.argv[2])

    # if not webserverHost or not webserverPort:
    #    print(f"{webserverHost}:{webserverPort} is not set")
    #    exit(-1)

    app.run(host='localhost', port=5000, debug=True)
