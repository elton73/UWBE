"""
Classes for specific experiments
"""

import datetime
import math
import os
import time
from time import localtime, strftime
from modules.tags import Data
import csv
from modules.accuracy import Accuracy

# Modified version of Tag class for is_moving experiment
class Tag_Moving(Accuracy):
    def __init__(self, tag_id):
        super(Accuracy, self).__init__()
        self.THRESHOLD = None # distance between two points in meters
        self.AVERAGING_WINDOW = None # number of datapoints to use for averaging
        self.TIMEFRAME = None # Time for comparing distance between two points in seconds

        self.tag_id = tag_id
        self.timestamp = None
        self.is_moving = None
        self.raw_time = None

        self.previous_time = None
        self.old_data = []

        self.average_position = None
        self.average_time = None
        self.average_distance_travelled = 0

        self.csv_file = None
        self.csv_writer = None

        self.is_moving_count = 0
        self.is_stationary_count = 0
        self.count = 0

        self.time_reference = None
        self.setup_complete = False

        self.time_begin_of_program = None
        self.data_points = 0
        self.update_rate = None
        self.index = None

        self.comments = None
        self.accuracy = None
        self.gold_standard = None

        #debug
        self.previous_averaging_time = None
        self.averaging_time = None
        self.moving_time = 0.0

    def add_data(self, data):
        try:
            accelerometer = data['data']['tagData']['accelerometer'][0]
        except:
            return
        self.data_points += 1
        coordinates = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        self.raw_time = time.perf_counter()
        self.update_rate = data['data']['metrics']['rates']['update']
        data = Data(coordinates, accelerometer, self.raw_time, self.update_rate)

        self.old_data.append(data)
        if len(self.old_data) <= (self.AVERAGING_WINDOW + 1):
            return
        self.old_data.pop(0)

        #Compare positions to determine if patient has moved
        data_time = self.old_data[self.index].raw_time

        #initialize data
        if not self.average_position:
            self.average_position = self.get_average_pos()
        if not self.previous_time:
            self.previous_time = data_time

        elif (data_time-self.previous_time) > self.TIMEFRAME:
            if not(self.setup_complete):
                print("Data Collection Has Begun")
            self.setup_complete = True
            if not self.time_begin_of_program:
                self.time_begin_of_program = time.perf_counter()
                self.time_reference = data_time

                #debug
                self.previous_averaging_time = time.perf_counter()

            average_position = self.get_average_pos()

            #debug
            self.averaging_time = time.perf_counter()

            self.average_distance_travelled = float(math.dist(average_position, self.average_position))/1000.0
            if self.average_distance_travelled > self.THRESHOLD and (not self.is_moving or self.is_moving is None):
                self.add_time()
                self.is_moving = True
            elif self.average_distance_travelled <= self.THRESHOLD and (self.is_moving or self.is_moving is None):
                self.add_time()
                self.is_moving = False

            self.previous_time = data_time
            self.average_position = average_position

        if self.setup_complete:
            if self.is_moving:
                self.is_moving_count += 1
            else:
                self.is_stationary_count += 1
            self.count += 1
            self.time_reference = data_time

        # debug
        if self.tag_id == "10001009" and self.setup_complete:
            print(
                f"Moving: {self.is_moving}, Distance Travelled: {self.average_distance_travelled}, "
                f"time_elapsed: {time.perf_counter()-self.time_begin_of_program}")

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
                               "experiments",
                               "moving_experiment",
                               "ILS",
                               datetime.date.today().strftime('%Y-%m-%d'))
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        tag_csv = os.path.join(csv_dir, f'{strftime("T%H-%M-%S", localtime())}.csv')
        self.csv_file = open(tag_csv, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, dialect='excel')
        self.csv_writer.writerow(['tag_id', 'comments', 'accuracy (moving_time)', 'Error (seconds)',
                                  'gold_standard_moving_time', 'moving_time', 'stationary_time', 'total_time',
                                  'window', 'threshold', 'timeframe', 'update rate', 'date recorded'])

    def get_output(self, gold_standard):
        self.gold_standard = gold_standard
        time_elapsed = self.old_data[self.index].raw_time - self.time_begin_of_program

        #debug
        if self.moving_time > time_elapsed:
            print("Error. Moving time is greater than time elapsed.")
            quit()

        if self.moving_time >= gold_standard:
            self.true_positives = gold_standard
            self.false_positives = self.moving_time - gold_standard
            self.true_negatives = time_elapsed-self.moving_time
            self.false_negatives = 0

        elif self.moving_time < gold_standard:
            self.true_positives = self.moving_time
            self.false_positives = 0
            self.true_negatives = time_elapsed-gold_standard
            self.false_negatives = gold_standard-self.moving_time
        self.accuracy = self.get_accuracy()

        try:
            print(f"Accuracy (decimal): {self.accuracy}, Time_elapsed: {time_elapsed}, Time Spent Moving: "
                  f"{self.moving_time}, Actual Time Moving: {gold_standard}, "
                  f", datapoints = {self.count}")

            if not self.csv_file:
                self.setup_csv()
            self.write_csv(time_elapsed)
            print("Writing to CSV...")
        except:
            print("Something Went Wrong Writing To CSV")

    def write_csv(self, time_elapsed):
        self.csv_writer.writerow(
            [self.tag_id, self.comments, self.accuracy, self.moving_time - self.gold_standard, self.gold_standard,
             self.moving_time, time_elapsed - self.moving_time, self.old_data[self.index].raw_time - self.time_begin_of_program,
             self.AVERAGING_WINDOW, self.THRESHOLD, self.TIMEFRAME, self.update_rate,
             self.old_data[self.index].timestamp])

    def set_variables(self, threshold, timeframe, window, comments):
        self.THRESHOLD = threshold
        self.TIMEFRAME = timeframe
        self.AVERAGING_WINDOW = window
        self.comments = comments
        self.is_moving_count = 0
        self.is_stationary_count = 0
        self.count = 0
        self.old_data = []
        self.time_reference = None
        self.time_begin_of_program = None
        self.index = int(self.AVERAGING_WINDOW/2)
        self.timestamp = None
        self.raw_time = None
        self.previous_time = None
        self.average_position = None
        self.average_time = None
        self.average_distance_travelled = 0
        self.s = None
        self.data_points = 0
        self.update_rate = None
        self.is_moving = None
        self.setup_complete = False
        self.gold_standard = None
        self.accuracy = None
        self.true_negatives = None
        self.true_positives = None
        self.false_positives = None
        self.false_negatives = None

        #debug
        self.averaging_time = None
        self.moving_time = 0.0
        self.change_in_movement = False

    def add_time(self):
        # debug. Change in movement
        if self.is_moving is None:
            return
        print(f"{time.perf_counter() - self.time_begin_of_program}")
        if self.is_moving:
            self.moving_time += (self.averaging_time - self.previous_averaging_time - 0.5 * self.TIMEFRAME)

        self.previous_averaging_time = self.averaging_time


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
