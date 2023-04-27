"""
Tag class for tracking all data
"""

import datetime
import numpy as np
import math
import os
from pathlib import Path
import path
from time import localtime, strftime
import csv

class Tag():
    def __init__(self, tag_id):
        self.THRESHOLD = 0.4 # distance between two points in meters
        self.WINDOW = 15 # number of datapoints to use for averaging
        self.TIMEFRAME = 5 # Time for comparing distance between two points in seconds

        self.tag_id = tag_id
        self.timestamp = None
        self.is_moving = False

        self.time_start = None
        self.old_data = []

        self.average_position = None
        self.average_time = None

        self.csv_file = None
        self.csv_writer = None
        self.setup_csv()
        self.s = None

    def add_data(self, data):
        try:
            accelerometer = data['data']['tagData']['accelerometer'][0]
        except:
            return
        coordinates = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        raw_time = data['timestamp']
        update_rate = data['data']['metrics']['rates']['update']
        data = Data(coordinates, accelerometer, raw_time, update_rate)

        self.old_data.append(data)
        if len(self.old_data) < self.WINDOW:
            return
        self.old_data.pop(0)

        #Compare positions every second to determine if patient has moved
        index = int(self.WINDOW/2)-1
        data_time = self.old_data[index].raw_time
        if not self.average_position:
            self.average_position = self.get_average_pos()
        if not self.time_start:
            self.time_start = data_time
        elif (data_time-self.time_start) > self.TIMEFRAME:
            average_position = self.get_average_pos()
            if float(math.dist(average_position, self.average_position))/1000.0 > self.THRESHOLD:
                self.is_moving = True
            else:
                self.is_moving = False
            self.time_start = data_time
            self.average_position = average_position

        # debug
        if self.tag_id == "10001009":
            print(
                f"Coordinates: [{self.old_data[index].coordinates}], Accel: {self.old_data[index].accelerometer}, "
                f"Moving: {self.is_moving}, Time: {self.old_data[index].timestamp}")

        self.csv_writer.writerow([self.tag_id, self.old_data[index].coordinates, self.old_data[index].accelerometer,
                                  self.is_moving, self.average_position, self.old_data[index].timestamp,
                                  self.old_data[index].timestamp])

    def get_average_pos(self):
        sum_x = 0
        sum_y = 0
        for i in self.old_data:
            sum_x += i.x
            sum_y += i.y
        return [sum_x/len(self.old_data), sum_y/len(self.old_data)]

    def setup_csv(self):
        csv_dir = os.path.join(os.getcwd(),
                               "csv",
                               self.tag_id,
                               datetime.date.today().strftime('%Y-%m-%d'))
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        tag_csv = os.path.join(csv_dir, f'{strftime("%H:%M:%S", localtime()).replace(":", "-")}.csv')
        self.csv_file = open(tag_csv, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, dialect='excel')
        self.csv_writer.writerow(['tag_id', 'coordinates', 'accelerometer', 'moving', 'average_position', 'timestamp',
                                  'update rate'])

class Data():
    def __init__(self, c, a ,r, u):
        self.coordinates = c
        self.x = c[0]
        self.y = c[1]
        self.accelerometer = a
        self.raw_time = r
        self.update_rate = u
        self.timestamp = self.get_timestamp()

    def get_timestamp(self):
        local_datetime = datetime.datetime.fromtimestamp(self.raw_time)
        return \
            f"{local_datetime.strftime('%H')}:" \
            f"{local_datetime.strftime('%M')}:" \
            f"{local_datetime.strftime('%S')}"



def tag_search(tags, tag_id):
    return next((tag for tag in tags if tag.tag_id == tag_id), False)

