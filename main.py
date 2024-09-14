import time
import datetime
import logging
import os, random
from threading import Thread
from flask import Flask, request, render_template_string
from lightning_sdk import Studio, Teamspace, Status

# Initialize Flask app
app = Flask(__name__)

# Configure logging
log_filename = 'LightingServer.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])

# Suppress Flask logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('flask').setLevel(logging.WARNING)

# Global variables
checks = []
started_time = datetime.datetime.now()

# HTML template with a textbox to input commands and a section to display the output
html_template = '''
    <html>
        <head>
            <title>Command Executor</title>
        </head>
        <body>
            <center><h1>Terminal Command Executor</h1></center>
            <form method="POST" action="/cmd">
                <textarea name="command" rows="5" cols="50" placeholder="Enter your command here"></textarea><br><br>
                <input type="submit" value="Run Command">
            </form>

            {% if output %}
                <h3>Output:</h3>
                <pre>{{ output }}</pre>
            {% endif %}

            {% if error %}
                <h3>Error:</h3>
                <pre>{{ error }}</pre>
            {% endif %}
        </body>
    </html>
'''

def cleanup():
    """Cleans up all existing studios."""
    try:
        teamspace = Teamspace('vision-model', user='spidyweeb')
        all_studios = teamspace.studios
        if all_studios:
            for studio in all_studios:
                try:
                    s = Studio(studio.name, teamspace='vision-model', user='spidyweeb')
                    logging.info(f"Deleting {studio.name} -- {s.status}")
                    s.delete()
                    time.sleep(2)
                except Exception as e:
                    logging.error(f"Failed to delete studio {studio.name}: {e}")
        return all_studios
    except Exception as e:
        logging.error(f"Error in cleanup: {e}")
        return None


def start_new():
    """Starts a new studio."""
    try:
        s = Studio(name=f"Chicken Bot {random.randrange(1, 100)}", teamspace='vision-model', user='spidyweeb', create_ok=True)
        s.start()
        time.sleep(2)
        while s.status == Status.Pending:
            time.sleep(2)
        global started_time
        started_time = datetime.datetime.now()
        return s, started_time
    except Exception as e:
        logging.error(f"Error in start_new: {e}")
        return None, None


@app.route('/')
def home():
    """Main route displaying the server status."""
    try:
        latest = checks[-1] if checks else "Just Started"
        uptime = (datetime.datetime.now() - started_time).total_seconds()
        return f"<center><h1>Server is running</h1></center><br><center><h2>Last Update: {latest}</h2></center><br><center><h2>Total Uptime: {uptime} Seconds</h2></center>"
    except Exception as e:
        logging.error(f"Error in home route: {e}")
        return "<center><h1>Error Occurred</h1></center>"


@app.route('/logs')
def logs():
    """Route displaying the server logs."""
    try:
        with open(log_filename, 'r') as f:
            log_content = f.read().replace('\n', '<br>')
        return f"<pre>{log_content}</pre>"
    except Exception as e:
        logging.error(f"Error in logs route: {e}")
        return "<center><h1>Error Occurred</h1></center>"


@app.route('/cmd', methods=['GET', 'POST'])
def command_executor():
    """Route for executing terminal commands and displaying the output or error."""
    output = None
    error = None
    if request.method == 'POST':
        command = request.form.get('command')

        # Ensure that a studio is running
        if new and new.status == Status.Running:
            try:
                # Run the command using the studio object
                output = new.run(command)
            except Exception as e:
                error = str(e)
        else:
            error = "No running studio instance available to run the command."

    return render_template_string(html_template, output=output, error=error)


def run_flask():
    """Runs the Flask server in a separate thread."""
    try:
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))
    except Exception as e:
        logging.error(f"Error in run_flask: {e}")

def keep_alive():
    """Keeps the Flask server running."""
    try:
        t = Thread(target=run_flask)
        t.daemon = True
        t.start()
    except Exception as e:
        logging.error(f"Error in keep_alive: {e}")

keep_alive()

try:
    new = None
    stud = cleanup()
    if stud:
        logging.info(stud)
    while True:
        try:
            if new and new.status == Status.Running:
                uptime_seconds = (datetime.datetime.now() - started_time).total_seconds()
                if uptime_seconds > 12400:  # Restart the server if uptime exceeds threshold
                    logging.info("Restart Server!!")
                    new.stop()
                    new.delete()
                    logging.info("Cleaning Old Servers...")
                    stud = cleanup()
                    time.sleep(3)
                    if stud:
                        logging.info("Output Is Fine")
                    logging.info("Starting New Server...")
                    new, started_time = start_new()
                else:
                    logging.info("Server is Running!!")
                    now = datetime.datetime.now()
                    checks.append(now)
                    output = new.run("sudo apt install screenfetch")
                    output = new.run("screenfetch -n -N")
                    logging.info("Pinged....")
            else:
                logging.info("Cleaning Old Server...")
                stud = cleanup()
                logging.info("Starting New Server...")
                new, started_time = start_new()
                if new and new.status == Status.Running:
                    logging.info("New Server Started ...")
                    logging.info("Installing the Bot !!")
                    new.run("wget https://gist.github.com/MrxAravind/057be3f62390036bd39427824a2492b4/raw/z.sh")
                    out = new.run("bash z.sh")
                    logging.info(out)           
                    print("Completed Installation...")
            time.sleep(60)
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
except Exception as e:
    logging.error(f"Unexpected error: {e}")
