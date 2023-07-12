"""
Class for analyzing the raw dataset V3
"""

from project.utils.tags import Data
import os
import csv
from matplotlib import pyplot as plt
from project.utils.accuracy import Accuracy
import config

class TagMovingV3(Accuracy):
    def __init__(self, tag_id):
        super(Accuracy, self).__init__()
        self.tag_id = tag_id
        self.csv_file = None
        self.csv_writer = None
        self.save_data = True
        self.comments = None
        self.speed_csv_file = None
        self.speed_csv_writer = None
        self.save_speeds = False
        self.setup_type = "1"
        # constants
        self.averaging_window_threshold = 5
        self.speed_threshold = 0.3  # min speed

        #reset
        self.is_moving = False
        self.moving_time = 0
        self.transition_count = 0
        self.total_time_elapsed = 0
        self.raw_data_buffer = []
        self.data_buffer = []
        self.start_of_movement_time = None
        self.end_of_movement_time = None
        self.accuracy = 0
        self.gold_standard_time = None
        self.gold_standard_transition_count = None
        self.gold_standard_intervals = []
        self.error = None
        self.moving_time_indexes = []
        self.moving_time_intervals = []
        self.index = 1
        self.start_index = None
        self.end_index = None
        self.start_of_program = None

        #plot
        self.speeds = []

    # add a data point and process it
    def add_data(self, raw_data):
        self.index += 1  # set index to track current data point

        # fill a data buffer. This buffer has the live data
        self.raw_data_buffer.append(raw_data)
        if len(self.raw_data_buffer) < self.averaging_window_threshold:
            return

        # use an averaging window to average the positioning data. The program will have a delay based on this window
        index = self.averaging_window_threshold // 2
        current_coordinate = self.raw_data_buffer[index]
        if not self.start_of_program:
            self.start_of_program = current_coordinate.raw_time

        data = Data(self.get_average_pos(), current_coordinate.accelerometer, current_coordinate.raw_time,
                    current_coordinate.update_rate)
        data.raw_coordinates = current_coordinate.coordinates

        self.raw_data_buffer.pop(0)
        data.index = self.index - index

        # fill another data_buffer that has the averaged coordinates. This buffer will be delayed
        if len(self.data_buffer) < 1:
            self.data_buffer.append(data)
            return

        # get the speed from averaged coordinates
        data.set_speed(self.data_buffer[-1])
        self.data_buffer.append(data)
        if len(self.data_buffer) > 2:
            self.data_buffer.pop(0)
        self.speeds.append(self.data_buffer[-1].speed)

        # save data to csv
        if self.save_speeds:
            self.write_speed_csv()

        self.evaluate_data()

    def get_average_pos(self):
        sum_x = 0
        sum_y = 0
        for i in self.raw_data_buffer:
            sum_x += i.x
            sum_y += i.y
        return [sum_x / len(self.raw_data_buffer), sum_y / len(self.raw_data_buffer)]

    # Calculate how long the tag has been moving based on speed data
    def evaluate_data(self):
        if not self.is_moving and self.data_buffer[-1].speed >= self.speed_threshold:
            self.start_of_movement_time = self.data_buffer[-1].raw_time
            self.start_index = self.data_buffer[-1].index
            self.is_moving = True
        elif self.is_moving and self.data_buffer[-1].speed < self.speed_threshold:
            self.end_of_movement_time = self.data_buffer[-1].raw_time
            moving_time = (self.end_of_movement_time - self.start_of_movement_time)
            self.is_moving = False
            self.transition_count += 1
            self.end_index = self.data_buffer[-1].index
            self.moving_time_indexes.append([self.start_index, self.end_index])
            self.moving_time += moving_time
            self.moving_time_intervals.append(round(moving_time, 2))

    # Find the accuracy of the program
    def get_output(self):
        if self.save_data and not self.csv_file:
            self.setup_csv()
        self.error = self.moving_time - self.gold_standard_time
        self.total_time_elapsed = self.data_buffer[-1].raw_time - self.start_of_program

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


    def write_csv(self):
        if self.save_data:
            self.csv_writer.writerow(
                [self.tag_id, self.comments, self.accuracy, self.error,
                 self.transition_count, self.gold_standard_transition_count, self.moving_time, self.gold_standard_time,
                 self.speed_threshold, self.averaging_window_threshold, self.total_time_elapsed,
                 self.data_buffer[-1].raw_time, self.moving_time_indexes, self.moving_time_intervals,
                 self.gold_standard_intervals])

    def write_speed_csv(self):
        if self.save_speeds:
            self.speed_csv_writer.writerow([self.comments, self.data_buffer[-1].speed, self.data_buffer[-1].coordinates,
                                            self.data_buffer[-1].index, self.data_buffer[-1].raw_time])

    def setup_speed_csv(self):
        if self.save_speeds:
            data_dir = os.path.join(config.PROJECT_DIRECTORY,
                                    "csv",
                                    self.tag_id,
                                    "experiments",
                                    "moving_experiment",
                                    "ILS",
                                    f"setup_{self.setup_type}",
                                    "Speeds")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            number = 1
            speed_csv = os.path.join(data_dir, f"Exp_{number}_Speeds.csv")
            while os.path.exists(speed_csv):
                number += 1
                speed_csv = os.path.join(data_dir, f"Exp_{number}_Speeds.csv")
            self.speed_csv_file = open(speed_csv, 'w', newline='')
            self.speed_csv_writer = csv.writer(self.speed_csv_file, dialect='excel')
            self.speed_csv_writer.writerow(['comments', "speed", "coordinates", "index"])

    def setup_csv(self):
        data_dir = os.path.join(config.PROJECT_DIRECTORY,
                                "csv",
                                self.tag_id,
                                "experiments",
                                "moving_experiment",
                                "ILS",
                                f"setup_{self.setup_type}",
                                "Results")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        number = 1
        tag_csv = os.path.join(data_dir, f"Exp_{number}_Results.csv")
        while os.path.exists(tag_csv):
            number += 1
            tag_csv = os.path.join(data_dir, f"Exp_{number}_Results.csv")
        self.csv_file = open(tag_csv, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['tag_id', 'comments', 'accuracy (moving_time)', 'Error (seconds)', 'Transitions',
                                  'gold_standard_transition_count', 'moving_time', 'gold_standard_moving_time',
                                  'speed_threshold', 'averaging_window', 'total_time', 'date recorded',
                                  'movement_intervals', 'gold_standard_movement_intervals'])

    # Reset the object instance when running a new experiment
    def reset(self, comments, exp_number):
        self.comments = comments
        self.is_moving = False
        self.moving_time = 0
        self.transition_count = 0
        self.total_time_elapsed = 0
        self.raw_data_buffer = []
        self.data_buffer = []
        self.start_of_movement_time = None
        self.end_of_movement_time = None
        self.accuracy = 0
        self.gold_standard_time = None
        self.gold_standard_transition_count = None
        self.error = None
        self.moving_time_indexes = []
        self.moving_time_intervals = []
        self.index = 1
        self.start_index = None
        self.end_index = None
        self.start_of_program = None
        self.gold_standard_intervals = []
        self.speeds = []

    def close_csv(self):
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
        if self.speed_csv_file:
            self.speed_csv_file.close()
            self.speed_csv_file = None

    def plot(self):
        time_range = []
        count = 0.0
        for i in range(len(self.speeds)):
            count += 0.1
            time_range.append(count)
        plt.plot(time_range, self.speeds)
        plt.show()