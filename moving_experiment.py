"""
Conduct a movement experiment here
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import keyboard
import paho.mqtt.client as mqtt
import json
import ssl
from modules.tags import Tag_Speed_Experiment, tag_search
import time
fail_count = 0
tag = None

class StartThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global running, tag

        tag_id = '10001009'
        is_moving = define_movement()
        threshold, timeframe, window = define_variables()
        tag = Tag_Speed_Experiment(tag_id, is_moving)
        tag.set_variables(threshold, timeframe, window)

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

                    save = str(input("Save (y/n)? "))
                    if 'y' in save:
                        tag.get_accuracy()
                    elif 'q' in save:
                        tag.csv_file.close()
                        quit()


                    tag.moving = define_movement()
                    threshold, timeframe, window = define_variables()
                    tag.set_variables(threshold, timeframe, window)
            elif keyboard.is_pressed('q'):
                client.loop_stop()
                if tag:
                    tag.csv_file.close()
                # print(f"Failed {fail_count} times")
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
    global running, fail_count, tag
    datas = json.loads(msg.payload.decode())
    for data in datas:
        if not running:
            continue
        if not data['success']:
            # print("Data Unsuccessful")
            # print(data)
            continue
        if not tag:
            continue
        tag.add_data(data)
        #     except Exception as e:
        #         print("Failed")
        #         print(e)
        #         print(data)
        #         fail_count += 1
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

def define_movement():
    moving = str(input("Are you moving (y/n)? "))
    if moving == 'y':
        is_moving = True
    elif moving == 'n':
        is_moving = False
    else:
        if tag:
            tag.csv_file.close()
        quit()
    return is_moving

def define_variables():
    threshold = float(input("Enter distance threshold in meters: "))
    if threshold == "q":
        if tag:
            tag.csv_file.close()
        quit()
    timeframe = float(input("Enter timeframe in seconds: "))
    if timeframe == "q":
        if tag:
            tag.csv_file.close()
        quit()
    window = float(input("Enter window length: "))
    if window == "q":
        if tag:
            tag.csv_file.close()
        quit()
    return threshold,timeframe,window

if __name__ == '__main__':
    StartThread().start()

# C:\Users\ML-2\Documents\GitHub\UWBE\venv\Scripts\python C:\Users\ML-2\Documents\GitHub\UWBE\speed_experiment.py