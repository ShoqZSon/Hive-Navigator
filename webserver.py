from flask import Flask, render_template, request, redirect, url_for
import sendData as sD

app = Flask(__name__)

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
    # TODO: location will need this as well
    tmp = destination.split(",")
    # TODO: Probably needs adaption since hard coding the elements to remove is inflexible
    tmp.pop(0)
    tmp.pop(3)
    destination = ",".join(tmp)

    # send the data to hivemind server
    sD.sendDataTo(location, destination, '127.0.0.1',65432)

    return redirect(url_for('success'))

@app.route('/success')
def success():
    """The /success route gets called when the task has been successfully transmitted
    It then proceeds to show the customer a map and an ETA of the robot towards their location
    """
    # TODO: Success page is supposed to show the current position of the bot + ETA

    return render_template('followBot.html')

if __name__ == '__main__':
    app.run(debug=True)
