"""
Class for retrieving a raw dataset for calibration
"""
import time
import os
import csv
from project.utils.accuracy import Accuracy
import config
from project.experiment_tools.zones import Zone

# Modified version of Tag class for a calibration experiment
class TagCalibration(Accuracy):
    def __init__(self, tag_id):
        super(Accuracy, self).__init__()
        self.tag_id = tag_id

        self.comments = None
        self.gold_standard_time = None
        self.gold_standard_transition_count = 0
        self.gold_standard_intervals = []
        self.coordinates = None
        self.zone = Zone()

        #  raw data csv
        self.enable_csv = True # set to true if saving a raw dataset
        self.csv_file = None
        self.csv_writer = None
        self.setup_type = None

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

