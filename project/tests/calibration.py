"""
Calibrate speed, distance, averaging variables (Deprecated)
"""

import math
import os
import ast
from project.experiment_tools.tags import Data
import csv
from project.utils.accuracy import Accuracy
import time
from project.utils.progress_bar import find_common_settings
import config


tag = None
date = None
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
        self.save_data = True

        self.is_moving_count = 0
        self.is_stationary_count = 0
        self.count = 0

        self.time_reference = None
        self.setup_complete = False

        self.start_of_program = None
        self.data_points = 0
        self.index = None

        self.comments = None
        self.accuracy = None
        self.gold_standard_time = None
        self.gold_standard_transitions = None

        self.previous_averaging_time = None
        self.averaging_time = None
        self.moving_time = 0.0
        self.transition_count = 0
        self.experiment_number = None
        self.error = 0.0
        self.start_of_movement = None

        self.gold_standard_transition_count = None
        self.gold_standard_time = None
        self.gold_standard_intervals = None
        self.moving_time_intervals = []
        self.setup_type = "1"

    def add_data(self, coordinates, accelerometer, raw_time, update_rate):
        if not self.csv_file and self.save_data:
            self.setup_csv()

        self.data_points += 1
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
            if not self.start_of_program:
                self.start_of_program = data_time
                self.time_reference = data_time
                self.previous_averaging_time = data_time

            average_position = self.get_average_pos()
            self.average_distance_travelled = float(math.dist(average_position, self.average_position)) / 1000.0
            self.averaging_time = data_time

            if self.average_distance_travelled > self.THRESHOLD and (not self.is_moving or self.is_moving is None):
                self.add_time()
                self.start_of_movement = self.averaging_time
                self.transition_count += 1
                self.is_moving = True
            elif self.average_distance_travelled <= self.THRESHOLD and (self.is_moving or self.is_moving is None):
                if self.is_moving:
                    self.moving_time_intervals.append((self.averaging_time - self.start_of_movement))
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
        if self.is_moving is None:
            return
        if self.is_moving:
            self.moving_time += (self.averaging_time - self.previous_averaging_time)
        self.previous_averaging_time = self.averaging_time
        self.average_distance_buffer = []

    def setup_csv(self):
        data_dir = os.path.join(os.getcwd(),
                                "../../csv",
                                self.tag_id,
                                "experiments",
                                "moving_experiment",
                                "ILS",
                                "setup_2",
                                "Calibration_1")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        tag_csv = os.path.join(data_dir, f"Exp_{self.experiment_number}_Results.csv")
        self.csv_file = open(tag_csv, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['tag_id', 'comments', 'accuracy (moving_time)', 'Error (seconds)', 'Transitions',
                                  'gold_standard_moving_time', 'gold_standard_moving_time', 'moving_time',
                                  'stationary_time', 'total_time', 'window', 'threshold', 'timeframe', 'update rate',
                                  'date recorded'])

    def close_csv(self):
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None

    def write_csv(self, time_elapsed):
        if self.save_data:
            self.csv_writer.writerow(
                [self.tag_id, self.comments, self.accuracy, self.error,
                 self.transition_count, self.gold_standard_transitions, self.gold_standard_time, self.moving_time, time_elapsed - self.moving_time,
                 self.old_data[self.index].raw_time - self.start_of_program,
                 self.AVERAGING_WINDOW, self.THRESHOLD, self.TIMEFRAME, self.old_data[self.index].update_rate,
                 self.old_data[self.index].timestamp])

    def set_variables(self, threshold, timeframe, window, comments, exp_number):
        self.THRESHOLD = threshold
        self.TIMEFRAME = timeframe
        self.AVERAGING_WINDOW = window
        self.comments = comments
        self.is_moving_count = 0
        self.is_stationary_count = 0
        self.count = 0
        self.old_data = []
        self.time_reference = None
        self.start_of_program = None
        self.index = int(self.AVERAGING_WINDOW / 2)
        self.timestamp = None
        self.previous_time = None
        self.average_position = None
        self.average_time = None
        self.average_distance_travelled = 0
        self.data_points = 0
        self.is_moving = None
        self.setup_complete = False
        self.gold_standard_time = None
        self.gold_standard_transitions = None
        self.accuracy = None
        self.true_negatives = None
        self.true_positives = None
        self.false_positives = None
        self.false_negatives = None
        self.averaging_time = None
        self.moving_time = 0.0
        self.average_distance_buffer = []
        self.transition_count = 0
        self.experiment_number = exp_number
        self.error = 0.0
        self.moving_time_intervals = []

    def get_output(self):
        if self.save_data and not self.csv_file:
            self.setup_csv()
        self.error = self.moving_time - self.gold_standard_time
        self.total_time_elapsed = self.old_data[-1].raw_time - self.start_of_program

        # get program accuracy
        if self.moving_time >= self.gold_standard_time:
            self.true_positives = self.gold_standard_time
            self.false_positives = self.moving_time - self.gold_standard_time
            self.true_negatives = self.total_time_elapsed - self.moving_time
            self.false_negatives = 0
        elif self.moving_time < self.gold_standard_time:
            self.true_positives = self.moving_time
            self.false_positives = 0
            self.true_negatives = self.total_time_elapsed - self.gold_standard_time
            self.false_negatives = self.gold_standard_time - self.moving_time
        self.accuracy = self.get_accuracy()

    # Check if any of the time interval errors are too large
    def find_error(self, max_error):
        if self.gold_standard_transition_count != self.transition_count:
            return True
        for i in range(int(self.gold_standard_transition_count)):
            if abs(float(self.gold_standard_intervals[i]) - float(self.moving_time_intervals[i])) > max_error:
                return True
        return False

def define_variables(tag):
    distance_threshold = None
    timeframe = None
    averaging_window = None

    valid_input = False
    while not valid_input:
        valid_input = True
        distance_threshold = input("Enter distance threshold in meters: ")
        if distance_threshold == "q":
            program_exit()
        try:
            distance_threshold = float(distance_threshold)
        except:
            print("Invalid distance threshold. Please enter float value.")
            valid_input = False
            continue

        timeframe = input("Enter timeframe in seconds: ")
        if timeframe == "q":
            program_exit()
        try:
            timeframe = float(timeframe)
        except:
            print("Invalid timeframe. Please enter float value.")
            valid_input = False
            continue

        averaging_window = input("Enter window length: ")
        if averaging_window == "q":
            if tag:
                program_exit()
        try:
            averaging_window = int(averaging_window)
        except:
            print("Invalid averaging_window. Please enter int value.")
            valid_input = False
            continue

    return distance_threshold, timeframe, averaging_window

def program_exit():
    global tag
    if tag and tag.csv_file:
        tag.close_csv()
    raise SystemExit

def main():
    global tag, counter

    # Enter inputs here
    tag_id = config.TAG_ID
    setup_type = "setup_2"
    save_data = False
    max_error = float(input("Enter Max Error: "))
    notes = input("Enter comments: ")

    indexes = []
    datasets = []
    tag = Tag_Moving(tag_id)
    tag.save_data = save_data
    tag.setup_type = setup_type
    # Input form to choose which datasets to analyze
    input_flag = False
    print("Enter s to begin or q to quit")
    while not input_flag:
        counter = str(input("Enter experiment number: "))
        if "q" in counter:  # quit calibration
            program_exit()
        elif "s" in counter:  # begin calibration
            input_flag = True
            if len(datasets) < 1:
                print("No data!")

        elif counter.isnumeric() and counter not in indexes:
            path = os.path.join(os.getcwd(),
                                config.PROJECT_DIRECTORY,
                                "csv",
                                tag_id,
                                "experiments",
                                "moving_experiment",
                                "ILS",
                                setup_type,
                                "raw_data",
                                f"Exp_{counter}.csv")
            if not os.path.exists(path):
                print(path)
                print("No such experiment! Please Try Again")
            else:
                file = open(path, "r")
                data = list(csv.reader(file, delimiter=","))
                file.close()
                datasets.append(data)
                indexes.append(counter)
        else:
            print("Invalid Input. Please Try Again")
    time_start = time.perf_counter()

    # Begin brute forcing for calibration settings
    settings = []

    # start and end settings for brute force method
    distance_threshold = 0.2
    timeframe = 0.5
    averaging_window = 1

    distance_threshold_max = 1.0
    timeframe_max = 3
    averaging_window_max = 20

    distance_threshold_increment = 0.05
    timeframe_increment = 0.1
    averaging_window_increment = 1
    progress_bar = 0.0
    progress_bar_max = int(len(indexes) * ((timeframe_max - timeframe) / timeframe_increment) *
                           (averaging_window_max - averaging_window + averaging_window_increment) /
                           averaging_window_increment)
    for i, dataset in zip(indexes, datasets):
        calibration_complete = False
        dataset.pop(0)
        gold_standard_intervals = ast.literal_eval(dataset.pop()[0])
        gold_standard_time = float(dataset.pop()[0])
        gold_standard_transition_count = float(dataset.pop()[0])

        best_settings = []
        update_progress_bar = True
        while not calibration_complete:
            tag.set_variables(distance_threshold, timeframe, averaging_window, f"Exp_{i}", i)

            tag.gold_standard_transition_count = gold_standard_transition_count
            tag.gold_standard_time = gold_standard_time
            tag.gold_standard_intervals = gold_standard_intervals

            for d in dataset:
                coordinates = ast.literal_eval(d[0])
                accelerometer = d[1]
                raw_time = float(d[2])
                update_rate = d[3]
                tag.add_data(coordinates, accelerometer, raw_time, update_rate)
            tag.add_time()
            tag.get_output()
            if not tag.find_error(max_error):
                best_settings.append((distance_threshold, timeframe, averaging_window))
            if update_progress_bar:
                print(f"\r{float(100*progress_bar / progress_bar_max):.2f} %", end='')
                update_progress_bar = False
            distance_threshold += distance_threshold_increment
            if distance_threshold > distance_threshold_max:
                distance_threshold = 0.2
                timeframe += timeframe_increment
                progress_bar += 1
                update_progress_bar = True
            if timeframe > timeframe_max:
                timeframe = 0.5
                averaging_window += averaging_window_increment
            if averaging_window > averaging_window_max:
                calibration_complete = True
                averaging_window = 1
        settings.append(best_settings)
        tag.close_csv()

        # break the loop if no settings are found
        if settings[int(i)-1] or len(find_common_settings(settings)) < 1:
            break

    print("\n")
    common_settings = find_common_settings(settings)
    time_taken = (time.perf_counter() - time_start)
    calibration_number = str(input("Enter calibration number: "))
    path = os.path.join(os.getcwd(),
                        "../../csv",
                        tag_id,
                        "experiments",
                        "moving_experiment",
                        "ILS",
                        setup_type,
                        f'calibration_total_{calibration_number}.csv')
    with open(path, 'w',newline='') as f:
        writer = csv.writer(f)
        for i in common_settings:
            writer.writerow(i)
        writer.writerow([f"Max Error {max_error}"])
        writer.writerow([f"{notes}"])

    print(f"Time Taken: {time_taken:.2f}")

if __name__ == '__main__':
    main()


