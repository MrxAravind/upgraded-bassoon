import time
import datetime
import logging
import os, random
from threading import Thread
from flask import Flask
from lightning_sdk import Studio, Teamspace, Status

# Initialize Flask app
app = Flask(__name__)

# Configure logging
log_filename = 'server.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])

# Global variables
checks = []
started_time = datetime.datetime.now()


def cleanup():
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
    try:
        latest = checks[-1] if checks else "Just Started"
        uptime = (datetime.datetime.now() - started_time).total_seconds()
        return f"<center><h1>Server is running</h1></center><br><center><h2>Last Update: {latest}</h2></center><br><center><h2>Total Uptime: {uptime} Seconds</h2></center>"
    except Exception as e:
        logging.error(f"Error in home route: {e}")
        return "<center><h1>Error Occurred</h1></center>"

@app.route('/logs')
def logs():
    try:
        with open(log_filename, 'r') as f:
            log_content = f.read().replace('\n', '<br>')
        return f"<pre>{log_content}</pre>"
    except Exception as e:
        logging.error(f"Error in logs route: {e}")
        return "<center><h1>Error Occurred</h1></center>"

def run_flask():
    try:
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))
    except Exception as e:
        logging.error(f"Error in run_flask: {e}")

def keep_alive():
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
                if uptime_seconds > 12400 :
                    logging.info("Restart Server!!")
                    new.stop()
                    new.delete()
                    logging.info("Cleaning Old Servers...")
                    stud = cleanup()
                    time.sleep(3)
                    if stud:
                        logging.info("Output Is Fine")
                    logging.info("Starting New Server..")
                    new, started_time = start_new()
                else:
                    logging.info("Server is Running!!")
                    now = datetime.datetime.now()
                    checks.append(now)
                    output = new.run("sudo apt install screenfetch")
                    output = new.run("screenfetch")
                    logging.info("Pinged....")
            else:
                logging.info("Cleaning Old Server...")
                stud = cleanup()
                logging.info("Starting New Server...")
                new, started_time = start_new()
                if new and new.status == Status.Running:
                    logging.info("New Server Started ...")
                    logging.info("Installing the Bot !!")
                    new.run("wget -qq https://gist.github.com/MrxAravind/f99ab9b5213d6c31b9f043494d007a59/raw/mltb.sh")
                    new.run("nohup sudo bash mltb.sh &")
                    print("Completed Instalation...")
            time.sleep(60)
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
except Exception as e:
    logging.error(f"Unexpected error: {e}")
