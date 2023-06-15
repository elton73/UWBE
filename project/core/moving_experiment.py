"""
Conduct a movement experiment here.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import keyboard
import paho.mqtt.client as mqtt
import json
import ssl
from project.experiment_tools.experiments import TagMoving
import time
import project.utils.inputs as inputs
from config import TAG_ID

# globals
running = False
tag = None

"""
Setup Pozyx Connection
"""
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
    global running, tag
    datas = json.loads(msg.payload.decode())
    for data in datas:
        if not running:
            continue
        if not data['success']:
            continue
        if not tag or data['tagId'] != tag.tag_id:
            print(f"Cannot find tag with tag id: {tag.tag_id}")
            continue
        print(data)
        tag.add_data(data)
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

"""
Threading
"""
class StartThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global running
        tag.comments = inputs.get_experiment_description(tag)
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

                    # user enters gold standard number of transitions
                    tag.gold_standard_transition_count = inputs.get_transition_count(tag)
                    # user enters gold standard moving time for each transition
                    tag.gold_standard_intervals = inputs.get_moving_time(tag)
                    tag.gold_standard_time = sum(tag.gold_standard_intervals)

                    tag.write_transitions_to_csv()
                    tag.write_time_to_csv()
                    tag.close_csv()
                    print("Results Saved!")

                    # user enters experiment description
                    tag.comments = inputs.get_experiment_description(tag)
                    print("\nPress control to start and stop. Press q to quit")


            elif keyboard.is_pressed('q'):
                client.loop_stop()
                if tag:
                    tag.close_csv()
                raise SystemExit

class AskQuestion(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def start(self):
        user_input = input("Ask Question")

if __name__ == '__main__':
    tag = TagMoving(TAG_ID)
    # tag = TagMoving(inputs.get_tag_id())
    StartThread().start()

# C:\Users\ML-2\Documents\GitHub\UWBE\venv\Scripts\python C:\Users\ML-2\Documents\GitHub\UWBE\moving_experiment.py