"""
Conduct a UWB accuracy experiment here
"""

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
                    process_and_save_data()
                    define_new_coordinates()
            elif keyboard.is_pressed('q'):
                client.loop_stop()
                quit()

#setup csv output
csv_dir = os.path.join(Path(r"/"), "../../csv", f"{datetime.date.today().strftime('%Y-%m-%d')}")
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)
path = os.path.join(csv_dir,
                    f'T{strftime("%H:%M:%S", localtime()).replace(":", "-")}.csv')
print(path)
csv_file = open(path, 'w', newline='')
csv_writer = csv.writer(csv_file, dialect='excel')
csv_writer.writerow(["coordinate number", "direction", "x_gold", "x_mean",
                     "x_largest_diff", "y_gold", "y_mean", "y_largest_diff", "Bad Signal"])

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
    global running, fails

    datas = json.loads(msg.payload.decode())
    for data in datas:
        if running:
            if data["tagId"] == "10001009":

                local_datetime = datetime.datetime.fromtimestamp(data['timestamp'])
                # Extract hours, minutes, and seconds from the local time
                hours = local_datetime.strftime('%H')
                minutes = local_datetime.strftime('%M')
                seconds = local_datetime.strftime('%S')
                current_time = f'{hours}:{minutes}:{seconds}'

                try:
                    coordinates = data['data']['coordinates']
                    x = coordinates['x']
                    y = coordinates['y']

                    x_list.append(x)
                    y_list.append(y)
                    print(coordinates)
                except:
                    print("No Coordinates")
                    fails += 1

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
x_list = []
y_list = []
x_gold = None
y_gold = None
coordinate = None
direction = None
fails = 0

#Glenrose Research Center coordinates with gold standard coordinates
def define_new_coordinates():
    global x_gold, y_gold, coordinate, direction, fails
    coordinate = str(input("Enter Coordinate Number: "))
    if coordinate == "q":
        csv_file.close()
        quit()
    elif coordinate == "1":
        x_gold = 1000
        y_gold = -1000

    elif coordinate == "2":
        x_gold = 3000
        y_gold = -1000

    elif coordinate == "3":
        x_gold = 2232
        y_gold = -5191

    elif coordinate == "4":
        x_gold = 232
        y_gold = -5191

    elif coordinate == "1_2":
        x_gold = 0
        y_gold = -1000

    elif coordinate == "3_4":
        x_gold = 0
        y_gold = -5191

    elif coordinate == "5_6":
        x_gold = 3232
        y_gold = 0

    elif coordinate == "7_8":
        x_gold = -268
        y_gold = -0

    else:
        x_gold = 0
        y_gold = 0

    direction = str(input("Enter Direction: "))
    fails = 0
    print("Press control to start and stop")

def process_and_save_data():
    global x_list, y_list, x_gold, y_gold, coordinate, direction, fails
    largest_diff_x = 0
    worst_x_coor = 0
    largest_diff_y = 0
    worst_y_coor = 0

    for coor in x_list:
        diff = coor - x_gold
        if abs(diff) > abs(largest_diff_x):
            largest_diff_x = diff
            worst_x_coor = coor

    for coor in y_list:
        diff = coor - y_gold
        if abs(diff) > abs(largest_diff_y):
            largest_diff_y = diff
            worst_y_coor = coor

    x_mean = statistics.mean(x_list)
    x_mode = statistics.mode(x_list)
    x_worst_coor = worst_x_coor
    x_largest_diff = largest_diff_x
    y_mean = statistics.mean(y_list)
    y_mode = statistics.mode(y_list)
    y_worst_coor = worst_y_coor
    y_largest_diff = largest_diff_y
    csv_writer.writerow([coordinate, direction, x_gold, x_mean, x_largest_diff, y_gold, y_mean, y_largest_diff, fails])
    x_list = []
    y_list = []

    print(f"x_mean = {x_mean}")
    print(f"x_mode = {x_mode}")
    print(f"x_worst_coor = {x_worst_coor}")
    print(f"x_largest_diff = {x_largest_diff}")
    print(f"y_mean = {y_mean}")
    print(f"y_mode = {y_mode}")
    print(f"y_worst_coor = {y_worst_coor}")
    print(f"y_largest_diff = {y_largest_diff}")

if __name__ == '__main__':
    define_new_coordinates()
    StartThread().start()

# C:\Users\ML-2\Documents\GitHub\UWBE\venv\Scripts\python C:\Users\ML-2\Documents\GitHub\UWBE\get_data.py