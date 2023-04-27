"""
Classes for specific experiments
"""

import datetime
import numpy as np
import math
import os
from pathlib import Path
import path
from time import localtime, strftime
from modules.tags import Data
import csv

# Modified version of Tag class for is_moving experiment
class Tag_Moving_Experiment():
    def __init__(self, tag_id, moving):
        self.moving = moving

        self.THRESHOLD = None # distance between two points in meters
        self.WINDOW = None # number of datapoints to use for averaging
        self.TIMEFRAME = None # Time for comparing distance between two points in seconds

        self.tag_id = tag_id
        self.timestamp = None
        self.is_moving = moving
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

        self.time_begin = None
        self.data_points = 0
        self.update_rate = None

    def add_data(self, data):
        try:
            accelerometer = data['data']['tagData']['accelerometer'][0]
        except:
            return
        self.data_points += 1
        coordinates = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        self.raw_time = data['timestamp']
        self.update_rate = data['data']['metrics']['rates']['update']
        data = Data(coordinates, accelerometer, self.raw_time, self.update_rate)

        self.old_data.append(data)
        if len(self.old_data) < self.WINDOW:
            return
        self.old_data.pop(0)

        #Compare positions to determine if patient has moved
        index = int(self.WINDOW/2)-1
        data_time = self.old_data[index].raw_time
        if not self.time_begin:
            self.time_begin = data_time
        if not self.average_position:
            self.average_position = self.get_average_pos()
        if not self.time_start:
            self.time_start = data_time
        elif (data_time-self.time_start) > self.TIMEFRAME:
            average_position = self.get_average_pos()
            self.temp = float(math.dist(average_position, self.average_position))/1000.0
            if float(math.dist(average_position, self.average_position))/1000.0 > self.THRESHOLD:
                self.is_moving = True
            else:
                self.is_moving = False
            self.time_start = data_time
            self.average_position = average_position
        if self.is_moving:
            self.is_moving_count += 1
        else:
            self.is_stationary_count += 1
        self.count += 1


        # debug
        if self.tag_id == "10001009":
            print(
                f"Moving: {self.is_moving}, Distance Travelled: {self.temp}, Average Pos: {self.average_position}, "
                f"Raw Pos: {self.old_data[int(self.WINDOW/2)-1].coordinates}")

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
                               "speed_experiment")
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        tag_csv = os.path.join(csv_dir, f'{strftime("%H:%M:%S", localtime()).replace(":", "-")}.csv')
        self.csv_file = open(tag_csv, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, dialect='excel')
        self.csv_writer.writerow(['tag_id', 'actually_moving', 'accuracy', 'time_elapsed', 'number_of_points',
                                  'is_moving_count', 'is_stationary_count', 'window', 'threshold', 'timeframe',
                                  'update rate'])

    def get_accuracy(self):
        print(self.is_moving_count)
        print(self.is_stationary_count)
        print(self.count)
        if self.moving:
            self.accuracy = float(self.is_moving_count/self.count)
            print(f"Accuracy (decimal): {self.accuracy}, Time_elapsed: {self.old_data[int(self.WINDOW/2)-1].raw_time-self.time_begin}, Datapoints: {self.count}")
        else:
            self.accuracy = float(self.is_stationary_count / self.count)
            print(f"Accuracy (decimal): {self.accuracy}, Time_elapsed: {self.old_data[int(self.WINDOW/2)-1].raw_time-self.time_begin}, Datapoints: {self.count}")


        self.csv_writer.writerow(
            [self.tag_id, self.moving, self.accuracy, self.old_data[int(self.WINDOW/2)-1].raw_time-self.time_begin,
             self.count, self.is_moving_count, self.is_stationary_count, self.WINDOW, self.THRESHOLD, self.TIMEFRAME,
             self.update_rate])
        print("Writing to CSV...")
        self.time_begin = None

    def set_variables(self, threshold, timeframe, window):
        self.THRESHOLD = threshold
        self.TIMEFRAME = timeframe
        self.WINDOW = window
        self.is_moving_count = 0
        self.is_stationary_count = 0
        self.count = 0



