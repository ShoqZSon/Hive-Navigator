from flask import Flask, render_template, request, redirect, url_for
import sendData as sD

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    location = request.form.get('location')
    destination = request.form.get('destination')
    # Process the form data here
    print(f"Location: {location}")
    print(f"Destination: {destination}")

    # implementation of sanitization here
    # ...
    print("Some sanitization happening here...")

    # send the data to hivemind server
    # receive sending response
    # proceed with showing the
    sD.send_data(location, destination, '127.0.0.1',65432)

    return redirect(url_for('success'))

@app.route('/success')
def success():
    # TODO: Success page is supposed to show the current position of the bot + ETA


    return render_template('followBot.html')

if __name__ == '__main__':
    app.run(debug=True)
