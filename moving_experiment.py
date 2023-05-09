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
from modules.experiments import Tag_Moving
import time

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
        if not tag or data['tagId'] != tag_id:
            print(f"Cannot find tag with tag id: {tag_id}")
            continue
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

        # experiment settings
        self.distance_threshold = None
        self.timeframe = None
        self.averaging_window = None
        self.comments = None
        self.gold_standard = None

    def run(self):
        global running
        self.define_variables()
        tag.set_variables(self.distance_threshold, self.timeframe, self.averaging_window, self.comments)
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

                    #debug
                    tag.add_time()
                    print(tag.moving_time)

                    save = str(input("Save (y/n)? "))
                    if 'y' in save:
                        self.define_gold_standard()
                        try:
                            tag.get_output(self.gold_standard)
                        except:
                            print("Save Failed")
                    elif 'q' in save:
                        if tag and tag.csv_file:
                            tag.csv_file.close()
                        raise SystemExit
                    self.define_variables()
                    tag.set_variables(self.distance_threshold, self.timeframe, self.averaging_window,
                                           self.comments)
            elif keyboard.is_pressed('q'):
                client.loop_stop()
                if tag and tag.csv_file:
                    tag.csv_file.close()
                raise SystemExit

    def define_variables(self):
        valid_input = False
        while not valid_input:
            valid_input = True
            distance_threshold = input("Enter distance threshold in meters: ")
            if distance_threshold == "q":
                if tag and tag.csv_file:
                    tag.csv_file.close()
                raise SystemExit
            try:
                self.distance_threshold = float(distance_threshold)
            except:
                print("Invalid distance threshold. Please enter float value.")
                valid_input = False
                continue

            timeframe = input("Enter timeframe in seconds: ")
            if timeframe == "q":
                if tag and tag.csv_file:
                    tag.csv_file.close()
                raise SystemExit
            try:
                self.timeframe = float(timeframe)
            except:
                print("Invalid timeframe. Please enter float value.")
                valid_input = False
                continue

            averaging_window = input("Enter window length: ")
            if averaging_window == "q":
                if tag:
                    if tag.csv_file:
                        tag.csv_file.close()
                raise SystemExit
            try:
                self.averaging_window = int(averaging_window)
            except:
                print("Invalid averaging_window. Please enter int value.")
                valid_input = False
                continue

            comments = input("Enter comments: ")
            if comments == "q":
                if tag and tag.csv_file:
                    tag.csv_file.close()
                raise SystemExit
            self.comments = comments

    def define_gold_standard(self):
        valid_input = False
        while not valid_input:
            user_input = input("How long was the tag actually moving (seconds)? ")
            if user_input == "q":
                if tag and tag.csv_file:
                    tag.csv_file.close()
                raise SystemExit
            try:
                gold_standard = float(user_input)
                if gold_standard >= (tag.old_data[tag.index].raw_time - tag.time_begin_of_program):
                    print(f"Warning! Gold standard time is greater than elapsed time.")
                    continue
                self.gold_standard = gold_standard
                valid_input = True
            except:
                print("Invalid Input. Please Enter A Decimal Number. Enter q to quit.")


if __name__ == '__main__':
    tag_id = input("Enter tag id: ")
    if tag_id == "q":
        raise SystemExit
    tag = Tag_Moving(tag_id)
    StartThread().start()

# C:\Users\ML-2\Documents\GitHub\UWBE\venv\Scripts\python C:\Users\ML-2\Documents\GitHub\UWBE\moving_experiment.py