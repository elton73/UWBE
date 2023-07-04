"""
Conduct a movement experiment here.
"""

import socket
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
from project.utils.pychromecast_handler import AudioPlayer
import config
from urllib.request import urlretrieve
from mutagen.mp3 import MP3

# globals
running = False
tag = None
stop_flag = False

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
        global running, stop_flag

        # Ask user for experiment description
        user_input = inputs.get_experiment_description()
        if user_input == "q":
            stop_flag = True
            return
        # writing test as the description doesn't generate a csv
        elif user_input == "test":
            tag.enable_csv = False
        tag.comments = user_input

        #Start all threads
        PlayAudio().start()
        client.loop_start()

        while not stop_flag:
            # start and stop recording data by pressing ctrl
            if keyboard.is_pressed('ctrl'):
                time.sleep(1.0)
                keyboard.release('ctrl')
                running = not running
                if running:
                    print('Started')
                else:
                    print('Stopped')

                    if tag.enable_csv:
                        # user enters gold standard number of transitions
                        user_input = inputs.get_transition_count()
                        if user_input == "q":
                            stop_flag = True
                            break
                        tag.gold_standard_transition_count = user_input

                        # user enters gold standard moving time for each transition
                        user_input = inputs.get_moving_time(tag)
                        if user_input == "q":
                            stop_flag = True
                            break
                        tag.gold_standard_intervals = user_input
                        tag.gold_standard_time = sum(tag.gold_standard_intervals)
                        tag.write_transitions_to_csv()
                        tag.write_time_to_csv()
                        print("Results Saved!")
                    tag.close_csv()
                    tag.enable_csv = True  # reset csv flag

                    # user enters experiment description
                    user_input = inputs.get_experiment_description()
                    if user_input == "q":
                        stop_flag = True
                        break
                    elif user_input == "test":
                        tag.enable_csv = False
                    tag.comments = user_input

                    print("\nPress control to start and stop. Press q to quit")

            #end program on q press
            elif keyboard.is_pressed('q'):
                stop_flag = True

        # stop connections and close files
        if tag:
            tag.close_csv()
        client.loop_stop()
        client.disconnect()

# Handles audio triggers
class PlayAudio(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.audio_player = AudioPlayer()
        self.previous_zone = None
        self._wait_duration = 0.0
        self.previous_time = None


    def run(self):
        while not stop_flag:
            time.sleep(1)
            if not tag:
                break
            if not running:
                continue
            print(tag.zone.name)

            # set a wait duration to prevent triggers while audio is playing
            if self._wait_duration <= 0:
                # Compare previous zone to current zone to control triggers
                if self.previous_zone != tag.zone.name:
                    self.previous_zone = tag.zone.name

                    # Play mp3 from url
                    url = self.get_url(tag.zone.name)
                    filename, headers = urlretrieve(url)
                    audio = MP3(filename)
                    self._wait_duration = audio.info.length
                    self.audio_player.play_url(url)

                    self.previous_time = time.time()
            else:
                self._wait_duration -= (time.time()-self.previous_time)
                self.previous_time = time.time()
    def get_url(self, zone):
        if zone == "Living Room":
            return f"http://{config.IPV4_ADDRESS}:5000/static/LivingRoom.mp3"

        if zone == "Kitchen":
            return f"http://{config.IPV4_ADDRESS}:5000/static/Kitchen.mp3"

        if zone == "Bedroom":
            return f"http://{config.IPV4_ADDRESS}:5000/static/Bedroom.mp3"

        if zone == "Washroom":
            return f"http://{config.IPV4_ADDRESS}:5000/static/Washroom.mp3"





if __name__ == '__main__':
    tag = TagMoving(config.TAG_ID)
    StartThread().start()

# C:\Users\ML-2\Documents\GitHub\UWBE\venv\Scripts\python C:\Users\ML-2\Documents\GitHub\UWBE\moving_experiment.py