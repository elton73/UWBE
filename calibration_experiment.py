"""
Conduct an experiment for calibrating thresholds and averaging windows.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import keyboard
import paho.mqtt.client as mqtt
import json
import ssl
from project.experiment_tools.tag_calibration import TagCalibration
import time
from project.utils.pychromecast_handler import AudioPlayer
import project.utils.inputs as inputs
import config
from urllib.request import urlretrieve
from mutagen.mp3 import MP3
from project.utils.urls import get_url
from project.utils.directory_handler import DirectoryHandler

# globals
tag = TagCalibration(config.TAG_ID)
dir_handler = DirectoryHandler()
running = False
stop_flag = False

# Toggle to save data in furniture detection format
furniture_detection_experiment = False
tag.furniture_detection_experiment = furniture_detection_experiment

def on_connect(client, userdata, flags, rc):
    print(mqtt.connack_string(rc))
    client.subscribe(config.topic)

# Callback triggered by a new Pozyx data packet
def on_message(client, userdata, msg):
    global running, tag
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
Threading
"""
class StartThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global running, stop_flag

        # Ask user for experiment description
        exp_description = inputs.get_experiment_description()
        if exp_description == "q":
            stop_flag = True
            return

        #get output directory to save csv
        out = dir_handler.choose_output_directory()
        if out == "q":
            stop_flag = True
            return

        if not furniture_detection_experiment:
            dir_handler.setup_csv("raw_data")
            dir_handler.write_csv([exp_description])
        else:
            dir_handler.setup_csv("furniture_detection")

        #Start all threads
        PlayAudio().start()
        client.loop_start()

        countdown = 5
        while not stop_flag:
            # start and stop recording data by pressing ctrl
            if keyboard.is_pressed('ctrl'):
                time.sleep(1.0)
                keyboard.release('ctrl')
                while countdown > 0:
                    print(countdown)
                    time.sleep(1)
                    countdown -= 1
                running = not running
                if running:
                    print('Started')
                else:
                    print('Stopped')
                    print("\nPress control to start and stop. Press q to quit")

            #end program on q press
            elif keyboard.is_pressed('q'):
                stop_flag = True

        # stop connections and close files
        client.loop_stop()
        client.disconnect()
        dir_handler.close_csvs()

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

# C:\Users\ML-2\Documents\GitHub\UWBE\venv\Scripts\python C:\Users\ML-2\Documents\GitHub\UWBE\project\core\calibration_experiment.py