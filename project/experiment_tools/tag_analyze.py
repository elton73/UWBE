"""
Class for analyzing the raw dataset. Averages the data everytime a new datapoint is entered.
"""

from project.utils.accuracy import Accuracy
from project.utils.timestamps import get_timestamp
from project.experiment_tools.data_processor_v1 import DataProcessorV1
from project.experiment_tools.data_processor_v2 import DataProcessorV2
import time


class TagAnalyzer(Accuracy):
    def __init__(self, tag_id, data_processor="1"):
        super(Accuracy, self).__init__()
        self.tag_id = tag_id
        self.exp_description = None

        # Select which data processing algorithm to use
        if data_processor == "1":
            self.data_processor = DataProcessorV1()
        elif data_processor == "2":
            self.data_processor = DataProcessorV2()

        self.csv_data_names = ['tag_id',
                               'exp_description',
                               'accuracy',
                               'true_positives',
                               'true_negatives',
                               'false_positives',
                               'false_negatives',
                               'moving_time',
                               'actual_moving_time',
                               'total_time',
                               'count_threshold',
                               'speed_threshold',
                               'averaging_window',
                               'date recorded']

        self.csv_data = []
        self._save_speed = False
        self.accuracy = None

    # add a data point and process it
    def add_data(self, raw_data):
        self.data_processor.add(raw_data)
        self.data_processor.process()
        if self._save_speed and self.data_processor.ready:
            self.get_speed_csv_data()

    # Find the accuracy of the program
    def get_output(self, zed_handler):
        self.reset_accuracy()
        self.data_processor.total_time_elapsed = \
            self.data_processor.dataset[-1].raw_time - self.data_processor.start_of_program
        for d in self.data_processor.all_data:
            zed_data = zed_handler.match_timestamps(d.raw_time)
            if zed_data.action_state == d.action_state:
                if d.action_state == "IDLE":
                    self.true_negatives += 1
                elif d.action_state == "MOVING":
                    self.true_positives += 1
            else:
                if d.action_state == "IDLE":
                    self.false_negatives += 1
                elif d.action_state == "MOVING":
                    self.false_positives += 1

        self.accuracy = self.get_accuracy()

        self.csv_data = [
            self.tag_id,
            self.exp_description,
            self.accuracy,
            self.true_positives,
            self.true_negatives,
            self.false_positives,
            self.false_negatives,
            self.data_processor.moving_time,
            zed_handler.total_moving_time,
            self.data_processor.total_time_elapsed,
            self.data_processor.count_threshold,
            self.data_processor.speed_threshold,
            self.data_processor.averaging_window_threshold,
            get_timestamp(time.time())
        ]

    def get_speed_csv_data(self):
        self.csv_data = [self.exp_description, self.data_processor.dataset[-1].speeds,
                         self.data_processor.dataset[-1].timestamps,
                         self.data_processor.dataset[-1].raw_coordinates]

    # change how data is saved to csv for speed dataset
    def speed_format(self):
        self.csv_data_names = ['exp_description', "speed", "timestamps", "raw_coordinates"]
        self._save_speed = True

    def activate_calibration_mode(self):
        self.data_processor.calibration = True

    def set_new_averaging_window(self, window):
        self.data_processor.averaging_window_threshold = window
