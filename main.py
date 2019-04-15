from gps import GPS
from rfcomm import RFCOMM
import time
import subprocess

print("STARTING...")

rf = RFCOMM()
gps = GPS()

subprocess.run(["hciconfig", "hci0", "piscan"])

while True:

    if rf.client_connected:
        data = gps.update()

        if data is not None:
            print("DATA: " + data)
            rf.send_data(data + "\r\n")
        time.sleep(0.1)
    else:
        gps.stop()
        print("WAIT FOR CLIENT...")
        rf.wait_for_client()
        print("CLIENT ACCEPTED")
        gps.start()
        print("ENABLE GPS")
