from lightning_sdk import Machine, Studio, JobsPlugin, MultiMachineTrainingPlugin
import time
from flask import Flask
from threading import Thread
import os
import datetime


app = Flask(__name__)


checks = []
started_time = datetime.datetime.now()

@app.route('/')
def home():
    if len(checks) != 0:
         latest = checks[-1]
    else:
         latest = "Fucking Now Bitch"
    return f"<center><h1>Server is running<h1><center><br><center><h2>Last Update :{latest}<h2><center><br><center><h2>Total UpTime :{( datetime.datetime.now() - started_time).total_seconds()} Secconds<h2><center>"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))

def keep_alive():
    t = Thread(target=run)
    t.start()

s = Studio(name="statutory-blue-cgbmi", teamspace="vision-model", user="mrxaravind")
new = s.duplicate()

keep_alive()

while True:
    if "Running" in str(new.status):
        if (started_time - datetime.datetime.now()).total_seconds() > 14000:
           new.stop()
           new.delete()
           new = s.duplicate()
        else:
            print("Server is Running")
            now = datetime.datetime.now()
            checks.append(now)
            new.run("neofetch")
    else:
        started_time = datetime.datetime.now()
        print("Starting Server...")
        new.start()
        new.run("wget https://gist.github.com/MrxAravind/f99ab9b5213d6c31b9f043494d007a59/raw/mltb.sh &&  bash mltb.sh")
        continue
    time.sleep(60)    
        
