"""
Classes for specific experiments
"""

import datetime
import math
import os
from time import localtime, strftime
from modules.tags import Data
import csv
from modules.accuracy import Accuracy
import time

# Modified version of Tag class for is_moving experiment
class Tag_Moving(Accuracy):
    def __init__(self, tag_id):
        super(Accuracy, self).__init__()
        self.tag_id = tag_id
        self.raw_data_csv_file = None
        self.raw_data_csv_writer = None

    def add_data(self, data):
        if not self.raw_data_csv_file:
            self.setup_csv()
        try:
            accelerometer = data['data']['tagData']['accelerometer'][0]
        except:
            return
        coordinates = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        raw_time = data['timestamp']
        update_rate = data['data']['metrics']['rates']['update']

        raw_data = [coordinates, accelerometer, raw_time, update_rate]
        self.raw_data_csv_writer.writerow(raw_data)

    def setup_csv(self):
        counter = 1
        data_dir = os.path.join(os.getcwd(),
                               "csv",
                               self.tag_id,
                               "experiments",
                               "moving_experiment",
                               "ILS",
                               datetime.date.today().strftime('%Y-%m-%d'),
                               f"Exp_{counter}")
        while os.path.exists(data_dir):
            counter += 1
            data_dir = os.path.join(os.getcwd(),
                                    "csv",
                                    self.tag_id,
                                    "experiments",
                                    "moving_experiment",
                                    "ILS",
                                    datetime.date.today().strftime('%Y-%m-%d'),
                                    f"Exp_{counter}")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        raw_data_csv = os.path.join(data_dir, f"raw_data.csv")
        self.raw_data_csv_file = open(raw_data_csv, 'w', newline='')
        self.raw_data_csv_writer = csv.writer(self.raw_data_csv_file, dialect='excel')

    def close_csv(self):
        self.raw_data_csv_file.close()

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
        self.raw_data_csv_file = None
        self.raw_data_csv_writer = None
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

        self.csv_writer.writerow([time.time(), x, y])
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
