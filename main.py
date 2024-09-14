import time
import datetime
import logging
import os, random
import threading
from flask import Flask
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
new = None
new_server_starting = False
started_time = datetime.datetime.now()
lock = threading.Lock()  # Thread lock to prevent race conditions

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

def start_new_thread():
    global new, started_time, new_server_starting
    try:
        s = Studio(name=f"Chicken Bot {random.randrange(1, 100)}", teamspace='vision-model', user='spidyweeb', create_ok=True)
        s.start()
        
        timeout = 60  # 1-minute timeout for server to start
        waited = 0
        while s.status == Status.Pending and waited < timeout:
            time.sleep(2)
            waited += 2
        
        if waited >= timeout:
            raise TimeoutError("Server failed to start within the timeout period.")
        
        with lock:
            started_time = datetime.datetime.now()
            new = s
        
        new_server_starting = False
        logging.info("New Server Started Successfully!")
    except Exception as e:
        logging.error(f"Error in start_new_thread: {e}")
        new_server_starting = False

@app.route('/')
def home():
    try:
        latest = checks[-1] if checks else "Just Started"
        with lock:
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
        t = threading.Thread(target=run_flask)
        t.start()  # Not daemon anymore
    except Exception as e:
        logging.error(f"Error in keep_alive: {e}")

keep_alive()

try:
    stud = cleanup()
    if stud:
        logging.info(stud)
    
    while True:
        try:
            if new and new.status == Status.Running:
                with lock:
                    uptime_seconds = (datetime.datetime.now() - started_time).total_seconds()
                
                if uptime_seconds > 12400:
                    logging.info("Restart Server!!")
                    new.stop()
                    new.delete()
                    logging.info("Cleaning Old Servers...")
                    stud = cleanup()
                    time.sleep(3)
                    if stud:
                        logging.info("Output Is Fine")
                    
                    logging.info("Starting New Server..")
                    new_server_starting = True
                    threading.Thread(target=start_new_thread).start()  # Start new server in a thread
                else:
                    logging.info("Server is Running!!")
                    now = datetime.datetime.now()
                    checks.append(now)
                    
                    # Add retries for commands
                    try:
                        new.run("sudo apt install screenfetch")
                        output = new.run("screenfetch")
                        logging.info(output)
                    except Exception as cmd_e:
                        logging.error(f"Error running commands on server: {cmd_e}")
                    
                    logging.info("Pinged....")
            else:
                if not new_server_starting:  # Check if a new server is already starting
                    logging.info("Cleaning Old Server...")
                    stud = cleanup()
                    logging.info("Starting New Server...")
                    new_server_starting = True
                    threading.Thread(target=start_new_thread).start()  # Start new server in a thread
                else:
                    logging.info("New server is already being started...")
            
            time.sleep(60)  # Reduced sleep to allow more frequent checks
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
except Exception as e:
    logging.error(f"Unexpected error: {e}")
