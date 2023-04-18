import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import csv
import keyboard
import paho.mqtt.client as mqtt
import json
import ssl
import datetime
from time import localtime, strftime
import time
from pathlib import Path
import statistics

class StartThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global running
        client.loop_start()
        while True:
            if keyboard.is_pressed('ctrl'):  # Check if ctrl is pressed
                time.sleep(1.0)
                keyboard.release('ctrl')
                running = not running  # Toggle the running state
                if running:
                    print('Started')
                else:
                    print('Stopped')
            elif keyboard.is_pressed('q'):
                client.loop_stop()
                quit()

# setup csv output
csv_dir = os.path.join(Path(r"C:\Users\ML-2\Documents\GitHub\UWBE"),
                       "csv",
                       f"{datetime.date.today().strftime('%Y-%m-%d')}",
                       "Experiments")
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)
#Create output csv
tag1_csv = os.path.join(csv_dir, f'10001009_T{strftime("%H:%M:%S", localtime()).replace(":", "-")}.csv')
tag2_csv = os.path.join(csv_dir, f'10001001_T{strftime("%H:%M:%S", localtime()).replace(":", "-")}.csv')

tag1_csv_file = open(tag1_csv, 'w', newline='')
tag1_csv_writer = csv.writer(tag1_csv_file, dialect='excel')
tag1_csv_writer.writerow(['tag_id', 'coordinates', 'zone', 'moving', 'current_time'])
tag2_csv_file = open(tag2_csv, 'w', newline='')
tag2_csv_writer = csv.writer(tag2_csv_file, dialect='excel')
tag2_csv_writer.writerow(['tag_id', 'coordinates', 'zone', 'moving', 'current_time'])

#setup connection
tenant_id = "63ee6a286f3dc2ff641a73e2"
api_key = "13e46ac5-9788-46d0-89a4-111db4e6d858"

host = "mqtt.cloud.pozyxlabs.com"
port = 443
topic = f"{tenant_id}/tags"
username = tenant_id
password = api_key

def on_connect(client, userdata, flags, rc):
    print(mqtt.connack_string(rc))
    client.subscribe(topic)

# Callback triggered by a new Pozyx data packet
def on_message(client, userdata, msg):
    global running

    datas = json.loads(msg.payload.decode())
    for data in datas:
        if running:
            if data['success']:
                try:
                    local_datetime = datetime.datetime.fromtimestamp(data['timestamp'])
                    current_time = \
                        f"{local_datetime.strftime('%H')}:" \
                        f"{local_datetime.strftime('%M')}:" \
                        f"{local_datetime.strftime('%S')}"
                    tag_id = data['tagId']
                    coordinates = data['data']['coordinates']
                    zone = data['data']['zones'][0]['name']
                    moving = data['data']['moving']
                    output = [tag_id, coordinates, zone, moving, current_time]
                    if tag_id == "10001009":
                        tag1_csv_writer.writerow(output)
                    elif tag_id == "10001001":
                        tag2_csv_writer.writerow(output)
                    if tag_id == "10001009":
                        print(zone)
                except:
                    print("No Data")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic!")

client = mqtt.Client(transport="websockets")
client.username_pw_set(username, password=password)

# sets the secure context, enabling the WSS protocol
client.tls_set_context(context=ssl.create_default_context())

# set callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(host, port=port)

#setup global variables
running = False

if __name__ == '__main__':
    StartThread().start()

# C:\Users\ML-2\Documents\GitHub\UWBE\venv\Scripts\python C:\Users\ML-2\Documents\GitHub\UWBE\conduct_experiment.py