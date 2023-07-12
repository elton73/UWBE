"""
Class for analyzing the raw dataset Version 7. Averages the data every couple points making sure to never reuse old
datapoints
"""

import os
import csv
from matplotlib import pyplot as plt
from project.utils.accuracy import Accuracy
import config
import math
from project.utils.data import DataNodeV7


class TagMovingV7(Accuracy):
    def __init__(self, tag_id):
        super(Accuracy, self).__init__()
        self.tag_id = tag_id
        self.experiment_number = None
        self.csv_file = None
        self.csv_writer = None
        self.save_data = True
        self.comments = None
        self.speed_csv_file = None
        self.speed_csv_writer = None
        self.save_speeds = False
        self.setup_type = "1"
        # constants
        self.BUFFER_LENGTH = 10
        self.version = "7"

        self.index = -1
        self.dataset = []
        self.duplicate_counter = 0
        self.buffer = []
        self.time_start = None
        self.time_begin_of_program = None

    # add a data point and process it

    def add_data(self, raw_data):
        self.index += 1
        data_node = DataNodeV7(coordinates=raw_data.coordinates,
                             index=self.index,
                             raw_time=raw_data.raw_time)
        # first coordinate will have zero speed
        if not self.dataset:
            self.dataset.append(data_node)
            self.time_begin_of_program = data_node.raw_time
            print(f"{data_node.coordinates} {data_node.raw_time - self.time_begin_of_program}")
            self.write_speed_csv(data_node)
            return
        self.buffer.append(data_node)
        if len(self.buffer) == self.BUFFER_LENGTH:
            previous_node = self.dataset[-1]
            averaged_coordinates = self.get_average_pos(self.buffer)
            data_node = DataNodeV7(coordinates=averaged_coordinates,
                                 index=self.index,
                                 raw_time=raw_data.raw_time)
            speed = self.get_speed(previous_node, data_node)
            data_node.speed = speed
            self.dataset.append(data_node)
            print(f"{data_node.coordinates} {data_node.raw_time - self.time_begin_of_program}")
            self.write_speed_csv(data_node)
            self.buffer = []

    def get_speed(self, node1, node2):
        distance = float(math.dist(node1.coordinates, node2.coordinates)) / 1000.0  # get distance in meters
        time_elapsed = node2.raw_time - node1.raw_time
        return float(distance / time_elapsed)

    def get_average_pos(self, buffer):
        sum_x = 0
        sum_y = 0
        for i in buffer:
            sum_x += i.coordinates[0]
            sum_y += i.coordinates[1]
        return [sum_x / len(self.buffer), sum_y / len(self.buffer)]

    def write_csv(self):
        if self.save_data:
            self.csv_writer.writerow(
                [self.tag_id, self.comments, self.accuracy, self.error,
                 self.transition_count, self.gold_standard_transition_count, self.moving_time, self.gold_standard_time,
                 self.count_threshold, self.speed_threshold, self.averaging_window_threshold, self.total_time_elapsed,
                 self.data_buffer[-1].raw_time, self.moving_time_indexes, self.moving_time_intervals,
                 self.gold_standard_intervals])

    def write_speed_csv(self, node):
        if self.save_speeds:
            self.speed_csv_writer.writerow([self.comments, node.speed, node.coordinates,
                                            node.index, node.raw_time])

    def setup_speed_csv(self):
        if self.save_speeds:
            data_dir = os.path.join(config.PROJECT_DIRECTORY,
                                    "csv",
                                    self.tag_id,
                                    "experimentsV5",
                                    "moving_experiment",
                                    "ILS",
                                    "Speeds",
                                    f"version_self.version")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            number = 1
            speed_csv = os.path.join(data_dir, f"Exp_{number}_Speeds.csv")
            while os.path.exists(speed_csv):
                number += 1
                speed_csv = os.path.join(data_dir, f"Exp_{number}_Speeds.csv")
            self.speed_csv_file = open(speed_csv, 'w', newline='')
            self.speed_csv_writer = csv.writer(self.speed_csv_file, dialect='excel')
            self.speed_csv_writer.writerow(['comments', "speed", "coordinates", "index", "time"])

    def setup_csv(self):
        data_dir = os.path.join(config.PROJECT_DIRECTORY,
                                "csv",
                                self.tag_id,
                                "experimentsV5",
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
                                  'count', 'speed_threshold', 'averaging_window', 'total_time', 'date recorded',
                                  'moving_time_indexes', 'movement_intervals', 'gold_standard_movement_intervals'])

    # Reset the object instance when running a new experiment
    def reset(self, comments, exp_number):
        pass

    def close_csv(self):
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
        if self.speed_csv_file:
            self.speed_csv_file.close()
            self.speed_csv_file = None

    def plot(self):
        speeds = []
        index = []
        for i in self.dataset:
            speeds.append(i.speed)
            index.append(i.index)
        plt.plot(index, speeds)
        plt.show()

