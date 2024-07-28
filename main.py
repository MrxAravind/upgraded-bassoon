from lightning_sdk import Studio
import time
import datetime
import logging
import os
from threading import Thread
from flask import Flask, render_template_string

# Initialize Flask app
app = Flask(__name__)

# Configure logging
log_filename = 'server.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])

# Global variables to be used in the Flask app
checks = []
started_time = datetime.datetime.now()

@app.route('/')
def home():
    if len(checks) != 0:
        latest = checks[-1]
    else:
        latest = "Just Started"
    uptime = (datetime.datetime.now() - started_time).total_seconds()
    return f"<center><h1>Server is running</h1></center><br><center><h2>Last Update: {latest}</h2></center><br><center><h2>Total Uptime: {uptime} Seconds</h2></center>"

@app.route('/logs')
def logs():
    with open(log_filename, 'r') as f:
        log_content = f.read().replace('\n', '<br>')
    return render_template_string(f"<pre>{log_content}</pre>")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))

# Function to start the Flask app in a separate thread
def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# Studio setup
s = Studio(name="statutory-blue-cgbmi", teamspace="vision-model", user="mrxaravind")
new = s.duplicate()

keep_alive()

while True:
    if "Running" in str(new.status):
        uptime_seconds = (datetime.datetime.now() - started_time).total_seconds()
        if uptime_seconds > 13500:
            logging.info("Restarting server after 13500 seconds of uptime.")
            new.stop()
            new.delete()
            new = s.duplicate()
            started_time = datetime.datetime.now()  # Reset started time after duplication
        else:
            logging.info("Server is Running")
            now = datetime.datetime.now()
            checks.append(now)
            output = new.run("apt install neofetch")
            output = new.run("neofetch")
            logging.info(output)
    else:
        logging.info("Starting Server...")
        new.start()
        output = new.run("wget https://gist.github.com/MrxAravind/f99ab9b5213d6c31b9f043494d007a59/raw/mltb.sh && bash mltb.sh")
        logging.info(output)
        started_time = datetime.datetime.now()  # Reset started time after starting
    time.sleep(60)
