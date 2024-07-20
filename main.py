from lightning_sdk import Machine, Studio, JobsPlugin, MultiMachineTrainingPlugin
import time
from flask import Flask
from threading import Thread
import os
import datetime


app = Flask(__name__)


checks = []


@app.route('/')
def home():
    if len(checks) != 0:
         latest = checks[-1]
    else:
         latest = "Fucking Now Bitch"
    return f"<h1>Server is running<h1>,<br><h2>Last Update :{latest}<h2>"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))

def keep_alive():
    t = Thread(target=run)
    t.start()

s = Studio(name="certain-fuchsia-4sky", teamspace="vision-model", user="iknowhim52")

keep_alive()

while True:
    if "Running" in str(s.status):
        print("Server is Running")
        now = datetime.datetime.now()
        checks.append(now)
        s.run("neofetch")
    else:
        print("Starting Server...")
        s.start()
        continue
    time.sleep(60)
