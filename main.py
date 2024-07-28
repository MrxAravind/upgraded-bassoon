import time
import datetime
import logging
import os, random 
from threading import Thread
from flask import Flask, render_template_string
from lightning_sdk import Studio,Teamspace,Status





# Initialize Flask app
app = Flask(__name__)

# Configure logging
log_filename = 'server.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])

# Global variables to be used in the Flask app
checks = []

def cleanup(): 
    try:
      teamspace = Teamspace('vision-model', user='mrxaravind')
      all_studios = teamspace.studios
      if len(all_studios) != 0:
         for studio in all_studios:
             s = Studio(studio.name, teamspace='vision-model',user='mrxaravind')
             logging.info(f"{studio.names}--{s.status}")
             s.delete()
             time.sleep(2)
      return all_studios
    except Exception as e:
      logging.error(e)
      return None

        
def start_new():
     s = Studio(name=f"Chicken Bot{random.randrange(1,100)}",teamspace='vision-model',user='mrxaravind', create_ok=True)
     s.start()
     time.sleep(2)
     logging.info(s.status)
     while s.status == Status.Pending:
          time.sleep(2)
     logging.info(s.status)
     started_time = datetime.datetime.now()
     return s,started_time



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

keep_alive()
stud = cleanup()
new,started_time = start_new()
logging.info("Starting New Server...")



while True:
    if Status.Running == new.status:        
        uptime_seconds = (datetime.datetime.now() - started_time).total_seconds()        
        if uptime_seconds > 13500:
            logging.info("Creating New Server")
            new.stop()
            new.delete()
            stud = cleanup()
            time.sleep(3)
            if stud:
                logging.info("Starting New Server...")
                new,started_time = start_new()
        else:
            logging.info("Server is Running")
            now = datetime.datetime.now()
            checks.append(now)
            output = new.run("apt install neofetch")
            output = new.run("neofetch")
            logging.info(output)
    else:
        logging.info("Starting New Server...")
        stud = cleanup()
        if stud:
           logging.info("Starting New Server...")
           new,started_time = start_new()
           if Status.Running == new.status:
              output = new.run("sudo curl https://gist.github.com/MrxAravind/f99ab9b5213d6c31b9f043494d007a59/raw/mltb.sh | sudo bash ")
              logging.info(output)
    time.sleep(60)
