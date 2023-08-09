"""
Class for generating a complete dataset for analysis (Incomplete)
"""

from project.utils.timestamps import get_timestamp
import time
from project.experiment_tools.zones import Zone
from project.experiment_tools.data_processor_v1 import DataProcessorV1
from project.utils.data import RawData


class Tag:
    def __init__(self, tag_id, patient_id):
        self.tag_id = tag_id
        self.patient_id = patient_id
        self.datetime = get_timestamp(time.time())

        self.csv_data_names = [
            "patient_id",
            "tag_id",
            "raw_coordinates",
            "averaged_coordinates",
            "accelerometer",
            "speed",
            "is_moving",
            "moving_time",
            "update_rate",
            "unix_time",
            "date recorded"
            ]
        self.csv_data = []

        self.coordinates = None
        self.accelerometer = None
        self.speed = 0.0
        self.unix_time = None
        self.update_rate = None
        self.zone = Zone()

        # calibration settings
        self.averaging_window_threshold = 25
        self.speed_threshold = 0.2
        self.count_threshold = 14

        # choose which data processing tool to use
        self.data_processor = DataProcessorV1()
        self.data_processor.averaging_window_threshold = self.averaging_window_threshold
        self.data_processor.speed_threshold = self.speed_threshold
        self.data_processor.count_threshold = self.count_threshold

        self.ready_flag = False
    def add_data(self, raw_data):
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

        data = self.data_processor.dataset[-1]
        self.csv_data = [
            self.patient_id,
            self.tag_id,
            data.raw_coordinates,
            data.coordinates,
            data.accelerometer,
            data.speed,
            self.data_processor.is_moving,
            self.data_processor.moving_time,
            data.update_rate,
            data.raw_time,
            self.datetime
            ]
