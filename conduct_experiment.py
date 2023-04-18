import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import keyboard
import paho.mqtt.client as mqtt
import json
import ssl
import datetime
from modules.csv import setup_csv
import time

tag1_csv_writer, tag2_csv_writer = setup_csv()
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
            if data:
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
                    x = coordinates['x']
                    y = coordinates['y']
                    z = coordinates['z']
                    success = data['success']
                    output = [tag_id, x, y, z, zone, moving, success, current_time]
                    if tag_id == "10001009":
                        tag1_csv_writer.writerow(output)
                    elif tag_id == "10001001":
                        tag2_csv_writer.writerow(output)
                    if tag_id == "10001009":
                        print(f"({x},{y},{z}) {success} {zone}")
                except:
                    print("No Data")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic!")
    print("Press control to start and stop. Press q to quit")

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