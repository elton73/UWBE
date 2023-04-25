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
        self.tag_id = tag_id
        self.coordinates = None
        self.timestamp = None
        self.is_moving = False
        self.accelerometer = None
        self.old_coordinates = []
        self.average_position = None
        self.csv_file = None
        self.csv_writer = None
        self.setup_csv()
        self.raw_time = None
        self.s = None

    def add_data(self, data):
        self.coordinates = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        self.old_coordinates.append(self.coordinates)
        if len(self.old_coordinates) > 5:
            self.old_coordinates.pop(0)
        try:
            self.accelerometer = data['data']['tagData']['accelerometer'][0]
        except:
            return
        self.is_moving = self.moving()
        self.raw_time = data['timestamp']
        local_datetime = datetime.datetime.fromtimestamp(data['timestamp'])
        self.timestamp = \
            f"{local_datetime.strftime('%H')}:" \
            f"{local_datetime.strftime('%M')}:" \
            f"{local_datetime.strftime('%S')}"

        #debug
        if self.tag_id == "10001001":
            print(f"Coordinates: {self.coordinates}, Accel: {self.accelerometer}, Moving: {self.is_moving}, Speed: {self.s} Time: {self.timestamp}")

        self.csv_writer.writerow([self.tag_id, self.coordinates, self.accelerometer, self.is_moving, self.s, self.timestamp])



    def moving(self):
        if len(self.old_coordinates) < 5:
            self.average_position = self.coordinates
            self.average_time = self.raw_time
            return False
        average_position = self.get_average_pos()
        d = float(math.dist(average_position, self.average_position)/1000)
        t = float(self.raw_time)-float(self.average_time)
        self.s = d/t
        # speed threshold of 0.5
        if self.s > 0.5:
            self.average_position = average_position
            self.average_time = self.raw_time
            return True
        else:
            self.average_position = average_position
            self.average_time = self.raw_time
            return False

    def get_average_pos(self):
        sum_x = 0
        sum_y = 0
        for i in self.old_coordinates:
            sum_x += i[0]
            sum_y += i[1]
        return [sum_x/len(self.old_coordinates), sum_y/len(self.old_coordinates)]

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
        self.csv_writer.writerow(['tag_id', 'coordinates', 'accelerometer', 'moving', 'speed', 'timestamp'])

def tag_search(tags, tag_id):
    return next((tag for tag in tags if tag.tag_id == tag_id), False)
