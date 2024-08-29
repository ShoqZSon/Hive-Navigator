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

    :returns -
    """
    location = request.form.get('location')
    destination = request.form.get('destination')
    # Process the form data here
    print(f"Location: {location}")
    print(f"Destination: {destination}")

    # get the coordinates of the location, destination and the level

    # implementation of sanitization here
    # ...
    print("Some sanitization happening here...")

    # send the data to hivemind server
    # receive sending response
    # proceed with showing the
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
