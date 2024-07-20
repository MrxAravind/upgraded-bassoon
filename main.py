from lightning_sdk import Machine, Studio, JobsPlugin, MultiMachineTrainingPlugin
import time


s = Studio(name="certain-fuchsia-4sky", teamspace="vision-model", user="iknowhim52")

while True:
    if "Running" in str(s.status):
        print("Server is Running")
        s.run("neofetch")
    else:
        print("Starting Server...")
        s.start()
        continue
    time.sleep(60)
