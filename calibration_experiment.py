"""
Conduct an experiment to generate a csv for analysis later.
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
import winsound

# globals
tag = TagCalibration(config.TAG_ID)
dir_handler = DirectoryHandler()
running = False
stop_flag = False
number_of_failures = 0
"""
Experiment types
-----------------
Furniture detection: Generates a dataset that may be used to verify the accuracy of the UWB based off a piece of 
furniture

UWB Noise: A timed stationary experiment that generates a dataset that may be used to verify the accurcy of the UWB based off 
a known coordinate 

Neither: Generates a raw dataset
"""
uwb_noise_experiment = True  # set to true if performing a uwb_noise_experiment
furniture_detection_experiment = False  # set to true if performing a furniture detection experiment
if furniture_detection_experiment:
    tag.furniture_detection_experiment = furniture_detection_experiment
""""""

"""
Pozyx connection setup
"""
###
def on_connect(client, userdata, flags, rc):
    print(mqtt.connack_string(rc))
    client.subscribe(config.topic)

# Callback triggered by a new Pozyx data packet
def on_message(client, userdata, msg):
    global running, tag, number_of_failures
    datas = json.loads(msg.payload.decode())
    for data in datas:
        if not running:
            continue
        if not data['success']:
            # print(f"Data unsuccessfully retrieved: {data['errorCode']}")
            # count how many times the UWB fails to retrieve data
            number_of_failures += 1
            continue
        # filter the data by the tag's id
        if not tag or data['tagId'] != tag.tag_id:
            print(f"Cannot find tag with tag id: {tag.tag_id}")
            continue

        # add the incoming data to the tag object and then write the data to a csv
        tag.add_data(data)
        output = tag.csv_data
        output.append(str(number_of_failures))
        dir_handler.write_csv(output)
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic!")
    print("Press control to start. Press q to quit.")

client = mqtt.Client(transport="websockets")
client.username_pw_set(config.username, password=config.password)

# sets the secure context, enabling the WSS protocol
client.tls_set_context(context=ssl.create_default_context())

# set callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(config.host, port=config.port)
###

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
        print("Choose Where To Save CSV.")
        out = dir_handler.choose_output_directory()
        if out == "q":
            stop_flag = True
            return

        # format csvs depending on the type of experiment being run
        if not furniture_detection_experiment:
            dir_handler.setup_csv("raw_data")
            dir_handler.write_csv([exp_description])
        else:
            dir_handler.setup_csv("furniture_detection")

        #Start all threads
        # PlayAudio().start()
        client.loop_start()

        # set beep settings
        duration = 500  # milliseconds
        freq = 440  # Hz

        # a timer from when the user clicks control to when the program starts reading UWB data
        countdown = 5
        while not stop_flag:
            # start and stop recording data by pressing ctrl
            if keyboard.is_pressed('ctrl'):
                time.sleep(1.0)
                keyboard.release('ctrl')
                while countdown > 0:
                    print("\r", countdown, end="")
                    time.sleep(1)
                    countdown -= 1
                # program begins recording UWB data here
                winsound.Beep(freq, duration)
                running = True
                start_time = time.time()
                if running:
                    print('Started')
                # change the behavior of the program depending on the type of experiment. A uwb_noise_experiment will
                # only run for 60 seconds while others may run indefinitely
                if uwb_noise_experiment:
                    time_elapsed = time.time() - start_time
                    i = 0
                    while time_elapsed < 60 and not stop_flag:
                        time_elapsed = time.time() - start_time
                        if time_elapsed > i:
                            print("\r", round(time_elapsed, 1), end="")
                            i += 1
                        if keyboard.is_pressed("q"):
                            stop_flag = True
                    winsound.Beep(freq, duration)
                    running = False
                    stop_flag = True

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
        # every second, check the zone of the tag and broadcast the location if the tag has changed zones
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