"""
Class for analyzing the raw dataset V2
"""

import os
import csv
from matplotlib import pyplot as plt
from project.utils.accuracy import Accuracy
import config
import math

class TagMovingV5(Accuracy):
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
        self.averaging_window_threshold = 5
        self.speed_threshold = 0.3  # min speed
        self.count_threshold = 8

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
        self.stationary_count = 0
        self.moving_count = 0
        self.count = 0
        self.index = -1
        self.start_index = None
        self.end_index = None
        self.start_of_program = None

        #new data
        self.dataset = []
        self.duplicate_counter = 0

    # add a data point and process it

    def add_data(self, raw_data):
        self.index += 1
        data_node = DataNode(coordinates=raw_data.coordinates,
                             index=self.index,
                             raw_time=raw_data.raw_time)
        # first coordinate will have zero speed
        if not self.dataset:
            self.dataset.append(data_node)
            self.write_speed_csv(data_node)
        else:
            previous_node = self.dataset[-1]
            # return if the new datapoint has the same coordinates and 0.5 seconds has not passed else calculate speed
            if not data_node.coordinates == previous_node.coordinates or (data_node.raw_time - previous_node.raw_time) >= 0.5:
                speed = self.get_speed(previous_node, data_node)
                data_node.speed = speed
                self.dataset.append(data_node)
                self.write_speed_csv(data_node)

    def get_speed(self, node1, node2):
        distance = float(math.dist(node1.coordinates, node2.coordinates)) / 1000.0 # get distance in meters
        time_elapsed = node2.raw_time-node1.raw_time
        return float(distance / time_elapsed)


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
                                  'moving_time_indexes',  'movement_intervals', 'gold_standard_movement_intervals'])

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
        time_range = []
        count = 0.0
        for i in self.dataset:
            speeds.append(i.speed)
            time_range.append(i.raw_time)
        plt.plot(time_range, speeds)
        plt.show()

class DataNode:
    def __init__(self, coordinates, index, raw_time, speed=0.0):
        self.coordinates = coordinates
        self.speed = speed
        self.index = index
        self.is_moving = False
        self.raw_time = raw_time

