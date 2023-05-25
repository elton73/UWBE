"""
Calibrate speed, distance, averaging variables
"""

import datetime
import math
import os
import ast
from modules.tags import Data
import csv
from modules.accuracy import Accuracy
import time


tag = None
# Modified version of Tag class for is_moving experiment
class Tag_Moving(Accuracy):
    def __init__(self, tag_id):
        super(Accuracy, self).__init__()
        self.THRESHOLD = None  # distance between two points in meters
        self.AVERAGING_WINDOW = None  # number of datapoints to use for averaging
        self.TIMEFRAME = None  # Time for comparing distance between two points in seconds

        self.tag_id = tag_id
        self.timestamp = None
        self.is_moving = None

        self.previous_time = None
        self.old_data = []

        self.average_position = None
        self.average_time = None
        self.average_distance_travelled = 0
        self.average_distance_buffer = []

        self.csv_file = None
        self.csv_writer = None

        self.is_moving_count = 0
        self.is_stationary_count = 0
        self.count = 0

        self.time_reference = None
        self.setup_complete = False

        self.time_begin_of_program = None
        self.data_points = 0
        self.index = None

        self.comments = None
        self.accuracy = None
        self.gold_standard = None

        self.previous_averaging_time = None
        self.averaging_time = None
        self.moving_time = 0.0

    def add_data(self, c, a, t, u):
        if not self.csv_file:
            self.setup_csv()

        self.data_points += 1
        accelerometer = a
        coordinates = c
        raw_time = t
        update_rate = u
        data = Data(coordinates, accelerometer, raw_time, update_rate)

        self.old_data.append(data)
        self.count += 1
        if len(self.old_data) <= (self.AVERAGING_WINDOW + 1):
            return
        self.old_data.pop(0)

        # Compare positions to determine if patient has moved
        data_time = self.old_data[self.index].raw_time

        # initialize data
        if not self.average_position:
            self.average_position = self.get_average_pos()
        if not self.previous_time:
            self.previous_time = data_time

        elif (data_time - self.previous_time) > self.TIMEFRAME:
            self.setup_complete = True
            if not self.time_begin_of_program:
                self.time_begin_of_program = data_time
                self.time_reference = data_time
                self.previous_averaging_time = data_time

            average_position = self.get_average_pos()
            self.average_distance_travelled = float(math.dist(average_position, self.average_position)) / 1000.0
            self.averaging_time = data_time

            if self.average_distance_travelled > self.THRESHOLD and (not self.is_moving or self.is_moving is None):
                self.add_time()
                self.is_moving = True
            elif self.average_distance_travelled <= self.THRESHOLD and (self.is_moving or self.is_moving is None):
                self.add_time()
                self.is_moving = False

            self.previous_time = data_time
            self.average_position = average_position
        if self.setup_complete:
            self.average_distance_buffer.append(self.average_distance_travelled)
            if self.is_moving:
                self.is_moving_count += 1
            else:
                self.is_stationary_count += 1
            self.time_reference = data_time

    def get_average_pos(self):
        sum_x = 0
        sum_y = 0
        for i in self.old_data:
            sum_x += i.x
            sum_y += i.y
        return [sum_x / len(self.old_data), sum_y / len(self.old_data)]

    def add_time(self):
        # debug. Change in movement
        if self.is_moving is None:
            return
        if self.is_moving:
            distance_travelled = sum(self.average_distance_buffer) / len(self.average_distance_buffer)
            if distance_travelled <= 2.1:  # No error correction. Better with slow/normal walking speed tags.
                self.moving_time += (self.averaging_time - self.previous_averaging_time)
            else:  # With error correction. Use with fast walking speed tags.
                self.moving_time += (self.averaging_time - self.previous_averaging_time - 0.5 * self.TIMEFRAME)

        self.previous_averaging_time = self.averaging_time
        self.average_distance_buffer = []

    def setup_csv(self):
        data_dir = os.path.join(os.getcwd(),
                                "csv",
                                self.tag_id,
                                "experiments",
                                "moving_experiment",
                                "ILS",
                                datetime.date.today().strftime('%Y-%m-%d'))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        tag_csv = os.path.join(data_dir, f'calibration.csv')
        self.csv_file = open(tag_csv, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, dialect='excel')
        self.csv_writer.writerow(['tag_id', 'comments', 'accuracy (moving_time)', 'Error (seconds)',
                                  'gold_standard_moving_time', 'moving_time', 'stationary_time', 'total_time',
                                  'window', 'threshold', 'timeframe', 'update rate', 'date recorded'])

    def close_csv(self):
        self.csv_file.close()

    def get_output(self, gold_standard):
        self.gold_standard = gold_standard
        time_elapsed = self.old_data[self.index].raw_time - self.time_begin_of_program

        # debug
        if self.moving_time > time_elapsed:
            print("Error. Moving time is greater than time elapsed.")
            quit()

        if self.moving_time >= gold_standard:
            self.true_positives = gold_standard
            self.false_positives = self.moving_time - gold_standard
            self.true_negatives = time_elapsed - self.moving_time
            self.false_negatives = 0

        elif self.moving_time < gold_standard:
            self.true_positives = self.moving_time
            self.false_positives = 0
            self.true_negatives = time_elapsed - gold_standard
            self.false_negatives = gold_standard - self.moving_time
        self.accuracy = self.get_accuracy()

        print(f"Accuracy (decimal): {self.accuracy}, Time_elapsed: {time_elapsed}, Time Spent Moving: "
              f"{self.moving_time}, Actual Time Moving: {gold_standard}, "
              f", datapoints = {self.count}")
        self.write_csv(time_elapsed)
        print("Writing to CSV...")

    def write_csv(self, time_elapsed):
        self.csv_writer.writerow(
            [self.tag_id, self.comments, self.accuracy, self.moving_time - self.gold_standard, self.gold_standard,
             self.moving_time, time_elapsed - self.moving_time,
             self.old_data[self.index].raw_time - self.time_begin_of_program,
             self.AVERAGING_WINDOW, self.THRESHOLD, self.TIMEFRAME, self.old_data[self.index].update_rate,
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
        self.index = int(self.AVERAGING_WINDOW / 2)
        self.timestamp = None
        self.previous_time = None
        self.average_position = None
        self.average_time = None
        self.average_distance_travelled = 0
        self.s = None
        self.data_points = 0
        self.is_moving = None
        self.setup_complete = False
        self.gold_standard = None
        self.accuracy = None
        self.true_negatives = None
        self.true_positives = None
        self.false_positives = None
        self.false_negatives = None
        self.averaging_time = None
        self.moving_time = 0.0
        self.average_distance_buffer = []

def define_variables(tag):
    distance_threshold = None
    timeframe = None
    averaging_window = None
    comments = None

    valid_input = False
    while not valid_input:
        valid_input = True
        distance_threshold = input("Enter distance threshold in meters: ")
        if distance_threshold == "q":
            if tag and tag.csv_file:
                tag.close_csv()
            raise SystemExit
        try:
            distance_threshold = float(distance_threshold)
        except:
            print("Invalid distance threshold. Please enter float value.")
            valid_input = False
            continue

        timeframe = input("Enter timeframe in seconds: ")
        if timeframe == "q":
            if tag and tag.csv_file:
                tag.close_csv()
            raise SystemExit
        try:
            timeframe = float(timeframe)
        except:
            print("Invalid timeframe. Please enter float value.")
            valid_input = False
            continue

        averaging_window = input("Enter window length: ")
        if averaging_window == "q":
            if tag:
                if tag.csv_file:
                    tag.close_csv()
            raise SystemExit
        try:
            averaging_window = int(averaging_window)
        except:
            print("Invalid averaging_window. Please enter int value.")
            valid_input = False
            continue

    return distance_threshold, timeframe, averaging_window

def define_gold_standard():
    valid_input = False
    gold_standard = None
    while not valid_input:
        user_input = input("How long was the tag actually moving (seconds)? ")
        if user_input == "q":
            if tag and tag.csv_file:
                tag.close_csv()
            raise SystemExit
        try:
            g = float(user_input)
            if g >= (tag.old_data[tag.index].raw_time - tag.time_begin_of_program):
                print(f"Warning! Gold standard time is greater than elapsed time.")
                continue
            gold_standard = g
            valid_input = True
        except:
            print("Invalid Input. Please Enter A Decimal Number. Enter q to quit.")
    return gold_standard

if __name__ == '__main__':
    tag = Tag_Moving("10001009")
    while 1:
        counter = str(input("Enter experiment number: "))
        if counter == "q":
            if tag and tag.csv_file:
                tag.close_csv()
            raise SystemExit

        path = os.path.join(os.getcwd(),
                            "csv",
                            "10001009",
                            "experiments",
                            "moving_experiment",
                            "ILS",
                            datetime.date.today().strftime('%Y-%m-%d'),
                            f"Exp_{counter}",
                            f"raw_data.csv")
        file = open(path, "r")
        datalist = list(csv.reader(file, delimiter=","))
        file.close()

        distance_threshold, timeframe, averaging_window = define_variables(tag)
        tag.set_variables(distance_threshold, timeframe, averaging_window, f"Exp_{counter}")

        c = None
        a = None
        rt = None
        u = None
        for d in datalist:
            c = ast.literal_eval(d[0])
            a = d[1]
            rt = float(d[2])
            u = d[3]
            tag.add_data(c, a, rt, u)
        tag.add_time()
        tag.get_output(define_gold_standard())

