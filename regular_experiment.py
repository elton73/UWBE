"""
Conduct a normal experiment here (Incomplete)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import keyboard
import paho.mqtt.client as mqtt
import json
import ssl
import time
import project.utils.inputs as inputs
from project.utils.pychromecast_handler import AudioPlayer
import config
from urllib.request import urlretrieve
from mutagen.mp3 import MP3
from project.utils.urls import get_url
from project.experiment_tools.tag import Tag
from project.utils.directory_handler import DirectoryHandler

#globals
running = False
stop_flag = False
dir_handler = DirectoryHandler()

"""
Connecting to client
"""
def on_connect(client, userdata, flags, rc):
    print(mqtt.connack_string(rc))
    client.subscribe(config.topic)

# Callback triggered by a new Pozyx data packet
def on_message(client, userdata, msg):
    global running
    datas = json.loads(msg.payload.decode())
    for data in datas:
        if not running:
            continue
        if not data['success']:
            print("Data unsuccessfully retrieved")
            continue
        if not tag or data['tagId'] != tag.tag_id:
            print(f"Cannot find tag with tag id: {tag.tag_id}")
            continue
        tag.add_data(data)
        dir_handler.write_csv(tag.csv_data)
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic!")
    print("Press control to start and stop. Press q to quit")

client = mqtt.Client(transport="websockets")
client.username_pw_set(config.username, password=config.password)

# sets the secure context, enabling the WSS protocol
client.tls_set_context(context=ssl.create_default_context())

# set callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(config.host, port=config.port)

"""
Threads
"""
#Main Thread
class StartThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global running, stop_flag, tag

        patient_id = inputs.get_patient_id()
        if patient_id == "q":
            quit()
        tag_id = inputs.get_tag_id()
        if tag_id == "q":
            quit()
        tag = Tag(tag_id, patient_id)

        dir_handler.choose_output_directory()
        dir_handler.setup_csv(f"{patient_id}")

        #Start all threads
        PlayAudio().start()
        client.loop_start()

        while not stop_flag:
            # Toggle the running state ctrl press
            if keyboard.is_pressed('ctrl'):
                time.sleep(1.0)
                keyboard.release('ctrl')
                running = not running
                if running:
                    print('Setting Up...')
                else:
                    print('Stopped')
            elif keyboard.is_pressed('q'):
                stop_flag = True

        # stop connections and close files
        client.loop_stop()
        client.disconnect()
        dir_handler.close_csvs()

#Audio Thread
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
                self.previous_zone = None
                self._wait_duration = 0.0
                self.previous_time = None
                continue
            print(tag.zone.name)

            # set a wait duration to prevent triggers while audio is playing
            if self._wait_duration <= 0:
                # Compare previous zone to current zone to control triggers
                if self.previous_zone != tag.zone.name:
                    self.previous_zone = tag.zone.name
                    if not tag.zone.name == "Out Of Bounds":
                        # Play mp3 from url
                        url = get_url(tag.zone.name)
                        filename, headers = urlretrieve(url)
                        audio = MP3(filename)
                        self._wait_duration = audio.info.length
                        self.audio_player.play_url(url)
                        self.previous_time = time.time()
            else:
                self._wait_duration -= (time.time()-self.previous_time)
                self.previous_time = time.time()

if __name__ == '__main__':
    StartThread().start()
