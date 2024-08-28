from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_task():
    location = request.form.get('location')
    destination = request.form.get('destination')

    # Process the form data here
    print(f"Location: {location}, Destination: {destination}")
    return redirect(url_for('success'))

@app.route('/success')
def task_send_successfully():
    # TODO: Success page is supposed to show the current position of the bot + ETA
    return render_template('followBot.html')

if __name__ == '__main__':
    app.run(debug=True)
