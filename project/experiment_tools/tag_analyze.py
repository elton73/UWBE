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
        if data_processor == "1":
            self.data_processor = DataProcessorV1()
        elif data_processor == "2":
            self.data_processor = DataProcessorV2()
        self.csv_data_names = ['tag_id',
                               'exp_description',
                               'accuracy (moving_time)',
                               'Error (seconds)',
                               'total_time',
                               'moving_time',
                               'gold_standard_moving_time',
                               'movement_intervals',
                               'gold_standard_movement_intervals',
                               'count_threshold',
                               'speed_threshold',
                               'averaging_window',
                               'date recorded']
        self.csv_data = []
        self._save_speed = False

        # evaluation
        self.error = None
        self.accuracy = None
        self.gold_standard_time = None
        self.gold_standard_intervals = None
        self.gold_standard_transitions = None

    # add a data point and process it
    def add_data(self, raw_data):
        self.data_processor.add(raw_data)
        self.data_processor.process()
        if self._save_speed and self.data_processor.ready:
            self.get_speed_csv_data()

    # Find the accuracy of the program
    def get_output(self):
        self.data_processor.total_time_elapsed = \
            self.data_processor.dataset[-1].raw_time - self.data_processor.start_of_program
        self.error = self.data_processor.moving_time - self.gold_standard_time

        # get accuracy from two data types: time and transition count
        if self.data_processor.moving_time >= self.gold_standard_time:
            self.true_positives = self.gold_standard_time
            self.false_positives = self.data_processor.moving_time - self.gold_standard_time
            self.true_negatives = self.data_processor.total_time_elapsed - self.data_processor.moving_time
            self.false_negatives = 0
        elif self.data_processor.moving_time < self.gold_standard_time:
            self.true_positives = self.data_processor.moving_time
            self.false_positives = 0
            self.true_negatives = self.data_processor.total_time_elapsed - self.gold_standard_time
            self.false_negatives = self.gold_standard_time - self.data_processor.moving_time
        accuracy_1 = self.get_accuracy()

        if self.data_processor.transition_count >= self.gold_standard_transitions:
            self.true_positives = self.gold_standard_transitions
            self.false_positives = self.data_processor.transition_count - self.gold_standard_transitions
            self.true_negatives = 0
            self.false_negatives = 0
        elif self.data_processor.transition_count < self.gold_standard_transitions:
            self.true_positives = self.data_processor.transition_count
            self.false_positives = 0
            self.true_negatives = 0
            self.false_negatives = self.gold_standard_transitions - self.data_processor.transition_count
        accuracy_2 = self.get_accuracy()
        self.accuracy = accuracy_1*accuracy_2

        self.csv_data = [
            self.tag_id,
            self.exp_description,
            self.accuracy,
            self.error,
            self.data_processor.total_time_elapsed,
            self.data_processor.moving_time,
            self.gold_standard_time,
            self.data_processor.moving_time_intervals,
            self.gold_standard_intervals,
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
