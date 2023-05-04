"""
Tag class for tracking all data
"""

import datetime
import math
import os
from time import localtime, strftime
import csv

class Tag():
    def __init__(self, tag_id):

        self.THRESHOLD = 0.6  # distance between two points in meters
        self.TIMEFRAME = 2  # Time for comparing distance between two points in seconds
        self.AVERAGING_WINDOW = 24  # number of datapoints to use for averaging

        self.tag_id = tag_id
        self.timestamp = None
        self.is_moving = False

        self.time_start = None
        self.old_data = []

        self.average_position = None
        self.average_time = None

        self.csv_file = None
        self.csv_writer = None
        self.index = int(self.AVERAGING_WINDOW/2)
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
        if len(self.old_data) < self.AVERAGING_WINDOW:
            return
        self.old_data.pop(0)

        #Compare positions every second to determine if patient has moved
        data_time = self.old_data[self.index].raw_time
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
                f"Coordinates: [{self.old_data[self.index].coordinates}], Accel: {self.old_data[self.index].accelerometer}, "
                f"Moving: {self.is_moving}, Time: {self.old_data[self.index].timestamp}")

        if not self.csv_file:
            self.setup_csv()
        self.write_csv()

    def write_csv(self):
        self.csv_writer.writerow([self.tag_id, self.old_data[self.index].coordinates, self.old_data[self.index].accelerometer,
                                  self.is_moving, self.average_position, self.old_data[self.index].timestamp,
                                  self.old_data[self.index].update_rate])

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
        tag_csv = os.path.join(csv_dir, f'{strftime("T%H-%M-%S", localtime())}.csv')
        self.csv_file = open(tag_csv, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, dialect='excel')
        self.csv_writer.writerow(['tag_id', 'coordinates', 'accelerometer', 'moving', 'average_position', 'datetime',
                                  'update rate'])

class Data():
    def __init__(self, c, a, r, u):
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
            f"{local_datetime.strftime('%Y')}-" \
            f"{local_datetime.strftime('%m')}-" \
            f"{local_datetime.strftime('%d T')}" \
            f"{local_datetime.strftime('%H')}-" \
            f"{local_datetime.strftime('%M')}-" \
            f"{local_datetime.strftime('%S')}"



def tag_search(tags, tag_id):
    return next((tag for tag in tags if tag.tag_id == tag_id), False)


