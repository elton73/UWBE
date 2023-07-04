"""
Classes for specific experiments
"""

import os
import csv
from matplotlib import path, pyplot as plt
from project.utils.accuracy import Accuracy
from project.experiment_tools.tags import Data
from collections import Counter
import config

# Modified version of Tag class for a moving experiment
class TagMoving(Accuracy):
    def __init__(self, tag_id):
        super(Accuracy, self).__init__()
        self.tag_id = tag_id
        self.csv_file = None
        self.csv_writer = None
        self.comments = None
        self.gold_standard_time = None
        self.gold_standard_transition_count = 0
        self.gold_standard_intervals = []
        self.coordinates = None
        self.zone = self.Zone()
        self.write_to_csv = True

    def add_data(self, data):
        if not self.csv_file and self.write_to_csv:
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
        if self.write_to_csv:
            self.csv_writer.writerow(raw_data)

    def setup_csv(self):
        counter = 1
        data_dir = os.path.join(config.PROJECT_DIRECTORY,
                                "csv",
                                self.tag_id,
                                "experiments",
                                "moving_experiment",
                                "ILS",
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

    def write_transitions_to_csv(self):
        self.csv_writer.writerow([self.gold_standard_transition_count])

    def write_time_to_csv(self):
        self.csv_writer.writerow([self.gold_standard_time])
        self.csv_writer.writerow([self.gold_standard_intervals])

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




class TagMovingV2(Accuracy):
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
        if len(self.data_buffer) > 20:  # set data_buffer to size of 20
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
        if self.data_buffer[-1].speed > self.speed_threshold:
            self.moving_count += 1
        else:
            self.moving_count -= 1
        self.count += 1

        if self.count == self.count_threshold:
            if self.moving_count > 0:
                if not self.is_moving:
                    self.start_of_movement_time = self.get_start_of_movement_time()
                self.is_moving = True
                self.moving_count = 0
                self.stationary_count = 0
            else:
                if self.is_moving:
                    self.end_of_movement_time = self.get_end_of_movement_time()
                    moving_time = self.end_of_movement_time - self.start_of_movement_time
                    if moving_time > 0:
                        self.moving_time += moving_time
                        self.moving_time_intervals.append(round(moving_time, 2))
                        self.transition_count += 1
                        self.moving_time_indexes.append([self.start_index, self.end_index])
                self.is_moving = False
                self.moving_count = 0
                self.stationary_count = 0
            self.count = 0

    def get_end_of_movement_time(self):
        for d in self.data_buffer:
            if d.speed < self.speed_threshold:
                datapoint = next(i for i in self.data_buffer if i.raw_coordinates == d.raw_coordinates)
                self.end_index = datapoint.index
                return datapoint.raw_time

    def get_start_of_movement_time(self):
        for d in reversed(self.data_buffer):
            if d.speed > self.speed_threshold:
                self.start_index = d.index
                return d.raw_time

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
                 self.count_threshold, self.speed_threshold, self.averaging_window_threshold, self.total_time_elapsed,
                 self.data_buffer[-1].timestamp, self.moving_time_indexes, self.moving_time_intervals,
                 self.gold_standard_intervals])

    def write_speed_csv(self):
        if self.save_speeds:
            self.speed_csv_writer.writerow([self.comments, self.data_buffer[-1].speed, self.data_buffer[-1].coordinates,
                                            self.data_buffer[-1].index])

    def setup_speed_csv(self):
        if self.save_speeds:
            data_dir = os.path.join(config.PROJECT_DIRECTORY,
                                    "csv",
                                    self.tag_id,
                                    "experiments",
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
            self.speed_csv_writer.writerow(['comments', "speed", "coordinates", "index"])

    def setup_csv(self):
        data_dir = os.path.join(config.PROJECT_DIRECTORY,
                                "csv",
                                self.tag_id,
                                "experiments",
                                "moving_experiment",
                                "ILS",
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
                                  'movement_intervals', 'gold_standard_movement_intervals'])

    # Reset the object instance when running a new experiment
    def reset(self, comments, exp_number):
        self.experiment_number = exp_number
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
        self.stationary_count = 0
        self.moving_count = 0
        self.count = 0
        self.index = 1
        self.start_index = None
        self.end_index = None
        self.start_of_program = None
        self.gold_standard_intervals = []

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






