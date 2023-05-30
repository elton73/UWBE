"""
Classes for specific experiments
"""

import datetime
import os
import csv
import time

from modules.accuracy import Accuracy

# Modified version of Tag class for a moving experiment
class Tag_Moving(Accuracy):
    def __init__(self, tag_id):
        super(Accuracy, self).__init__()
        self.tag_id = tag_id
        self.csv_file = None
        self.csv_writer = None
        self.comments = None
        self.actual_time = None
        self.actual_transitions = 0
        self.route = "0"

    def add_data(self, data):
        if not self.csv_file:
            self.setup_csv()
        try:
            accelerometer = data['data']['tagData']['accelerometer'][0]
        except:
            return
        coordinates = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        raw_time = data['timestamp']
        # raw_time = time.perf_counter()
        update_rate = data['data']['metrics']['rates']['update']

        raw_data = [coordinates, accelerometer, raw_time, update_rate]
        self.csv_writer.writerow(raw_data)

    def setup_csv(self):
        counter = 1
        data_dir = os.path.join(os.getcwd(),
                                "csv",
                                self.tag_id,
                                "experiments",
                                "moving_experiment",
                                "ILS",
                                datetime.date.today().strftime('%Y-%m-%d'))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        csv_file = os.path.join(data_dir, f"Route_{self.route}-Exp_{counter}.csv")
        while os.path.exists(csv_file):
            counter += 1
            csv_file = os.path.join(data_dir, f"Route_{self.route}-Exp_{counter}.csv")
        self.csv_file = open(csv_file, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, dialect='excel')
        self.csv_writer.writerow([self.comments])

    def close_csv(self):
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None

    def write_time_to_csv(self):
        self.csv_writer.writerow([self.actual_time])

    def write_transitions_to_csv(self):
        self.csv_writer.writerow([self.actual_transitions])

