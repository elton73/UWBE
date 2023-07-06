"""
Class for retrieving a raw dataset
"""
import time
import os
import csv
from matplotlib import path, pyplot as plt
from project.utils.accuracy import Accuracy
from collections import Counter
import config

# Modified version of Tag class for a moving experiment
class TagMoving(Accuracy):
    def __init__(self, tag_id):
        super(Accuracy, self).__init__()
        self.tag_id = tag_id

        self.comments = None
        self.gold_standard_time = None
        self.gold_standard_transition_count = 0
        self.gold_standard_intervals = []
        self.coordinates = None
        self.zone = self.Zone()

        #  raw data csv
        self.enable_csv = True # set to true if saving a raw dataset
        self.csv_file = None
        self.csv_writer = None
        self.setup_type = "setup_2"

        #  furniture detection for positioning accuracy
        self.enable_furniture_detection = False  # set to true if saving a furniture detection dataset
        self.furniture_csv_file = None
        self.furniture_csv_writer = None

    def add_data(self, data):
        if self.enable_furniture_detection and not self.furniture_csv_file:
            self.setup_furniture_detection_csv()
        if not self.csv_file and self.enable_csv:
            self.setup_csv()
        try:
            accelerometer = data['data']['tagData']['accelerometer'][0]
        except:
            return
        self.coordinates = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        self.zone.get(self.coordinates)
        raw_time = data['timestamp']
        update_rate = data['data']['metrics']['rates']['update']

        raw_data = [self.coordinates, accelerometer, raw_time, update_rate, self.zone.name]
        if self.enable_csv:
            self.csv_writer.writerow(raw_data)
        if self.enable_furniture_detection:
            self.write_furniture_detection_csv()
    def setup_csv(self):
        counter = 1
        data_dir = os.path.join(config.PROJECT_DIRECTORY,
                                "csv",
                                self.tag_id,
                                "experiments",
                                "moving_experiment",
                                "ILS",
                                self.setup_type,
                                "raw_data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        csv_file = os.path.join(data_dir, f"Exp_{counter}.csv")
        while os.path.exists(csv_file):
            counter += 1
            csv_file = os.path.join(data_dir, f"Exp_{counter}.csv")
        self.csv_file = open(csv_file, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([self.comments])

    def close_csv(self):
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
        if self.furniture_csv_file:
            self.furniture_csv_file.close()
            self.furniture_csv_file = None

    def write_transitions_to_csv(self):
        self.csv_writer.writerow([self.gold_standard_transition_count])

    def write_time_to_csv(self):
        self.csv_writer.writerow([self.gold_standard_time])
        self.csv_writer.writerow([self.gold_standard_intervals])

    def setup_furniture_detection_csv(self):
        counter = 1
        data_dir = os.path.join(config.PROJECT_DIRECTORY,
                                "csv",
                                self.tag_id,
                                "experiments",
                                "furniture_detection",
                                "ILS",
                                self.setup_type)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        csv_file = os.path.join(data_dir, f"Exp_{counter}.csv")
        while os.path.exists(csv_file):
            counter += 1
            csv_file = os.path.join(data_dir, f"Exp_{counter}.csv")
        self.furniture_csv_file = open(csv_file, 'w', newline='')
        self.furniture_csv_writer = csv.writer(self.furniture_csv_file)

    def write_furniture_detection_csv(self):
        self.furniture_csv_writer.writerow([time.time(), self.coordinates[0], self.coordinates[1]])

    class Zone:
        def __init__(self):
            self.name = None
            self.previous_name = None
            self.zone_buffer = []

            self.kitchen = path.Path([
                (6449, 2910), (7908, 5473), (10287, 4885), (9639, 2057)
            ])
            self.living_room = path.Path([
                (419, 4446), (5027, 3282), (4809, 1537), (6438, 1333), (6448, 2910), (7907, 5473), (8343, 6482),
                (10407, 8228), (9200, 9668), (6699, 7631), (2624, 10001), (1287, 7484)
            ])
            self.bedroom = path.Path([
                (419, 4445), (5026, 3282), (4808, 1537), (5716, 1409), (5556, 0), (18, 30), (67, 2348)
            ])
            self.washroom = path.Path([
                (6449, 2909), (9639, 2056), (9519, 9), (5557, 0), (5717, 1409), (6439, 1333)
            ])

        def get(self, coordinates):
            if not coordinates:
                name = "No Coordinates"
            elif self.living_room.contains_point(coordinates):
                name = "Living Room"
            elif self.kitchen.contains_point(coordinates):
                name = "Kitchen"
            elif self.bedroom.contains_point(coordinates):
                name = "Bedroom"
            elif self.washroom.contains_point(coordinates):
                name = "Washroom"
            else:
                name = "Out Of Bounds"

            self.zone_buffer.append(name)
            # Find the mode of the last 5 zones and that will be the current zone
            if len(self.zone_buffer) < 6:
                self.name = name
                return
            self.zone_buffer.pop(0)
            self.name = self.mode(self.zone_buffer)

        @staticmethod
        def mode(zones):
            # Count the occurrences of each element
            counter = Counter(zones)

            # Find the maximum count
            max_count = max(counter.values())

            # Find all elements with the maximum count (the modes)
            mode = next(k for k, v in counter.items() if v == max_count)
            return mode






