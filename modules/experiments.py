"""
Classes for specific experiments
"""

import datetime
import numpy as np
import math
import os
from pathlib import Path
import path
import time
from time import localtime, strftime
from modules.tags import Data
import csv

# Modified version of Tag class for is_moving experiment
class Tag_Moving_Experiment():
    def __init__(self, tag_id, moving):
        self.moving = moving

        self.THRESHOLD = None # distance between two points in meters
        self.AVERAGING_WINDOW = None # number of datapoints to use for averaging
        self.TIMEFRAME = None # Time for comparing distance between two points in seconds

        self.tag_id = tag_id
        self.timestamp = None
        self.is_moving = None
        self.raw_time = None

        self.time_start = None
        self.old_data = []

        self.average_position = None
        self.average_time = None
        self.temp = 0

        self.csv_file = None
        self.csv_writer = None
        self.setup_csv()
        self.s = None

        self.accuracy = 0
        self.is_moving_count = 0
        self.is_stationary_count = 0
        self.count = 0

        self.moving_time = 0.0
        self.stationary_time = 0.0
        self.time_reference = None
        self.setup_complete = False

        self.time_begin = None
        self.data_points = 0
        self.update_rate = None
        self.index = None

        self.tested_speed = None

    def add_data(self, data):
        # try:
        #     accelerometer = data['data']['tagData']['accelerometer'][0]
        # except:
        #     return
        self.data_points += 1
        coordinates = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        self.raw_time = data['timestamp']
        self.update_rate = data['data']['metrics']['rates']['update']
        data = Data(coordinates, 0, self.raw_time, self.update_rate)

        self.old_data.append(data)
        if len(self.old_data) < self.AVERAGING_WINDOW:
            return
        self.old_data.pop(0)

        #Compare positions to determine if patient has moved
        data_time = self.old_data[self.index].raw_time
        if not self.time_begin:
            self.time_begin = data_time
        if not self.time_reference:
            self.time_reference = data_time
        if not self.average_position:
            self.average_position = self.get_average_pos()
        if not self.time_start:
            self.time_start = data_time
        elif (data_time-self.time_start) > self.TIMEFRAME:
            self.setup_complete = True
            average_position = self.get_average_pos()
            self.temp = float(math.dist(average_position, self.average_position))/1000.0
            if float(math.dist(average_position, self.average_position))/1000.0 > self.THRESHOLD:
                self.is_moving = True
            else:
                self.is_moving = False
            self.time_start = data_time
            self.average_position = average_position
        if self.setup_complete:
            if self.is_moving:
                self.is_moving_count += 1
                self.moving_time += (data_time - self.time_reference)
            else:
                self.is_stationary_count += 1
                self.stationary_time += (data_time-self.time_reference)
            self.count += 1
            self.time_reference = data_time


        # debug
        if self.tag_id == "10001009":
            print(
                f"Moving: {self.is_moving}, Distance Travelled: {self.temp}, Average Pos: {self.average_position}, "
                f"Raw Pos: {self.old_data[self.index].coordinates}")

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
                               "moving_experiment",
                               "ILS")
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        tag_csv = os.path.join(csv_dir, f'{strftime("%H:%M:%S", localtime()).replace(":", "-")}.csv')
        self.csv_file = open(tag_csv, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, dialect='excel')
        self.csv_writer.writerow(['tag_id', 'walking_speed', 'actually_moving', 'accuracy', 'time_elapsed',
                                  'number_of_points', 'is_moving_count', 'is_stationary_count', 'moving_time',
                                  'stationary_time', 'window', 'threshold', 'timeframe', 'update rate', 'datetime'])

    def get_accuracy(self):
        print(self.is_moving_count)
        print(self.is_stationary_count)
        print(self.count)
        try:
            if self.moving:
                self.accuracy = float(self.is_moving_count/self.count)
                print(f"Accuracy (decimal): {self.accuracy}, Time_elapsed: "
                      f"{self.old_data[self.index].raw_time - self.time_begin}, Datapoints: {self.count}, "
                      f"Time Spent Moving: {self.moving_time}")
            else:
                self.accuracy = float(self.is_stationary_count / self.count)
                print(f"Accuracy (decimal): {self.accuracy}, Time_elapsed: "
                      f"{self.old_data[self.index].raw_time - self.time_begin}, Datapoints: {self.count}, "
                      f"Time Spent Staionary: {self.stationary_time}")
            self.write_csv()
            print("Writing to CSV...")
        except:
            print("Something Went Wrong")

    def write_csv(self):
        self.csv_writer.writerow(
            [self.tag_id, self.tested_speed, self.moving, self.accuracy, self.old_data[self.index].raw_time - self.time_begin,
             self.count, self.is_moving_count, self.is_stationary_count, self.moving_time, self.stationary_time,
             self.AVERAGING_WINDOW, self.THRESHOLD, self.TIMEFRAME, self.update_rate,
             self.old_data[self.index].timestamp])

    def set_variables(self, threshold, timeframe, window, speed):
        self.THRESHOLD = threshold
        self.TIMEFRAME = timeframe
        self.AVERAGING_WINDOW = window
        self.tested_speed = speed
        self.is_moving_count = 0
        self.is_stationary_count = 0
        self.count = 0
        self.old_data = []
        self.moving_time = 0.0
        self.stationary_time = 0.0
        self.time_reference = None
        self.time_begin = None
        self.index = int(self.AVERAGING_WINDOW/2)
        self.timestamp = None
        self.raw_time = None
        self.time_start = None
        self.average_position = None
        self.average_time = None
        self.temp = 0
        self.s = None
        self.accuracy = 0
        self.data_points = 0
        self.update_rate = None
        self.is_moving = None
        self.setup_complete = False
class Tag_Positioning():
    def __init__(self, tag_id):
        self.THRESHOLD = 0.4 # distance between two points in meters
        self.AVERAGING_WINDOW = 15 # number of datapoints to use for averaging
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
        self.index = None
        self.s = None

    def add_data(self, data):
        try:
            accelerometer = data['data']['tagData']['accelerometer'][0]
        except:
            return
        x, y = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        raw_time = data['timestamp']
        # debug
        if self.tag_id == "10001009":
            print(
                f"Coordinates: [{x}, {y}], Time: {time.time()}")
        self.write_csv(time.time(), x, y)

    def write_csv(self, timestamp, x, y):
        self.csv_writer.writerow([timestamp, x, y])
    def setup_csv(self):
        csv_dir = os.path.join(os.getcwd(),
                               "csv",
                               self.tag_id,
                               "experiments",
                               "Hayden",
                               datetime.date.today().strftime('%Y-%m-%d'))
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        tag_csv = os.path.join(csv_dir, f'{strftime("T%H-%M-%S", localtime())}.csv')
        self.csv_file = open(tag_csv, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, dialect='excel')

# if __name__ == '__main__':
#     print(time.time())
