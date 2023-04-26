import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import keyboard
import paho.mqtt.client as mqtt
import json
import ssl
from modules.tags import Tag, tag_search
import time
fail_count = 0
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
    global running, fail_count
    datas = json.loads(msg.payload.decode())
    for data in datas:
        if not running:
            continue
        if not data['success']:
            print("Data Unsuccessful")
            print(data)
            continue
        tag = tag_search(tags, data['tagId'])
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

if __name__ == '__main__':
    tags = []
    inputs = True
    while inputs:
        tag = str(input("Enter s to start. Enter a tagId: "))
        if tag == 's':
            inputs = False
        else:
            tags.append(Tag(tag))

    if tags:
        StartThread().start()

# C:\Users\ML-3\Documents\GitHub\UWBE\venv\Scripts\python C:\Users\ML-3\Documents\GitHub\UWBE\conduct_experiment.py