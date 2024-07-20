from lightning_sdk import Machine, Studio, JobsPlugin, MultiMachineTrainingPlugin
import time
from flask import Flask
from threading import Thread
import os

app = Flask(__name__)


checks = []

os.system("export LIGHTNING_USER_ID=c4a99537-57d8-4320-baa4-286d3f38b044")
os.system("export LIGHTNING_API_KEY=10327400-e843-4a36-bbf0-6809d046826e")
os.system("lightning login")


@app.route('/')
def home():
    latest = checks[-1]
    return f"Server is running,\nLate Update :{latest}"

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
        now = time.time()
        checks.append(now)
        s.run("neofetch")
    else:
        print("Starting Server...")
        s.start()
        continue
    time.sleep(60)
