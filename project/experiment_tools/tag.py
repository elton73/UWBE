"""
Class for generating a complete dataset for analysis
"""

import os
import config
from project.utils.timestamps import get_timestamp
import time
import csv
from project.experiment_tools.zones import Zone
from project.experiment_tools.experimentsV2 import DataProcessorV2
from project.utils.data import RawData


class Tag:
    def __init__(self, tag_id, patient_id):
        self.tag_id = tag_id
        self.patient_id = patient_id
        self.datetime = get_timestamp(time.time())

        self.coordinates = None
        self.accelerometer = None
        self.speed = 0.0
        self.unix_time = None
        self.update_rate = None

        self.moving_time = 0.0
        self.total_time_elapsed = 0.0
        self.transition_count = 0.0
        self.zone = Zone()

        self.csv_file = None
        self.csv_writer = None
        self.setup_type = None

        # buffers
        self.raw_data_buffer = []
        self.processed_data_buffer = []

        # calibration settings
        self.averaging_window_threshold = 25
        self.speed_threshold = 0.2
        self.count_threshold = 14

        # choose which data processing tool to use
        self.data_processor = DataProcessorV2(self.averaging_window_threshold, self.speed_threshold,
                                              self.count_threshold)

        self.ready_flag = False
    def add_data(self, raw_data):
        # generate output csv file
        if not self.csv_file:
            self.setup_csv()

        # save incoming data
        try:
            self.accelerometer = raw_data['data']['tagData']['accelerometer'][0]
        except:
            self.accelerometer = []
        self.coordinates = [raw_data['data']['coordinates']['x'], raw_data['data']['coordinates']['y']]
        self.zone.get(self.coordinates)
        self.unix_time = raw_data['timestamp']
        self.update_rate = raw_data['data']['metrics']['rates']['update']
        raw_data = RawData(self.coordinates, self.accelerometer, self.unix_time, self.update_rate)

        self.data_processor.add(raw_data)
        self.data_processor.process()
        if not self.data_processor.ready:
            return
        if not self.ready_flag:
            print("Started")
            self.ready_flag = True
        self.write_csv()

    def setup_csv(self):
        directory = os.path.join(config.PROJECT_DIRECTORY,
                                 "csv",
                                 self.patient_id,
                                 self.tag_id)
        if not os.path.exists(directory):
            os.makedirs(directory)

        csv_file = os.path.join(directory, f"{self.datetime}.csv")
        self.csv_file = open(csv_file, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([
            "patient_id",
            "tag_id",
            "raw_coordinates",
            "averaged_coordinates",
            "accelerometer",
            "speed",
            "is_moving",
            "moving_time",
            "update_rate",
            "unix_time"
        ])

    def write_csv(self):
        data = self.data_processor.data_buffer[-1]
        self.csv_writer.writerow([
            self.patient_id,
            self.tag_id,
            data.raw_coordinates,
            data.coordinates,
            data.accelerometer,
            data.speed,
            self.data_processor.is_moving,
            self.data_processor.moving_time,
            data.update_rate,
            data.raw_time
        ])

    def close_csv(self):
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
