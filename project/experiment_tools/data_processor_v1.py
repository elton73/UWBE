"""
Data processor version 1 (Best Performance). Averages every data point
"""

from project.utils.data import DataNode

class DataProcessorV1:
    def __init__(self):

        self.averaging_window_threshold = 25
        self.speed_threshold = 0.2
        self.count_threshold = 14

        self.version = "1"

        self.index = self.averaging_window_threshold // 2
        self.current_data_point = None
        self.raw_data_buffer = []
        self.dataset = []
        self.start_of_program = None
        self.count = 0
        self.moving_count = 0
        self.stationary_count = 0
        self.transition_count = 0
        self.moving_time = 0.0
        self.is_moving = False
        self.start_of_movement_time = None
        self.end_of_movement_time = None
        self.total_time_elapsed = None
        self.ready = False

        # calibration settings
        self.calibration = False
        self.moving_time_intervals = []
        # plotting
        self.speeds = []
        self.timestamps = []

        # save all data for evaluating later
        self.all_data = []

    def add(self, raw_data):
        self.raw_data_buffer.append(raw_data)

    def process(self):
        # fill data buffer with raw coordinates
        if len(self.raw_data_buffer) < self.averaging_window_threshold:
            return
        self.current_data_point = self.raw_data_buffer[self.index]
        self.raw_data_buffer.pop(0)
        if not self.start_of_program:
            self.start_of_program = self.current_data_point.raw_time

        # create a data object
        data = DataNode(self.get_average_pos(), self.current_data_point.accelerometer,
                        self.current_data_point.raw_time,
                        self.current_data_point.update_rate)
        if self.is_moving:
            data.action_state = "MOVING"
        data.raw_coordinates = self.current_data_point.coordinates

        # fill data buffer with averaged coordinates
        if len(self.dataset) < 1:
            self.dataset.append(data)
            self.all_data.append(data)
            if self.calibration:
                self.speeds.append(data.speed)
                self.timestamps.append(data.raw_time)
            return

        # Once all buffers are filled, script is ready to process data
        self.ready = True
        # get the speed from averaged coordinates
        data.set_speed(self.dataset[-1])
        self.dataset.append(data)
        self.all_data.append(data)
        if self.calibration:
            self.speeds.append(data.speed)
            self.timestamps.append(data.raw_time)
        if len(self.dataset) > self.count_threshold:
            self.dataset.pop(0)
        self.evaluate_data()

    def evaluate_data(self):
        if self.dataset[-1].speed > self.speed_threshold:
            self.moving_count += 1
        else:
            self.moving_count -= 1
        self.count += 1

        if self.count == self.count_threshold:
            if self.moving_count > 0:
                if not self.is_moving:
                    self.start_of_movement_time = self.get_start_of_movement_time()
                self.is_moving = True
            else:
                if self.is_moving:
                    self.end_of_movement_time = self.get_end_of_movement_time()
                    moving_time = round(self.end_of_movement_time - self.start_of_movement_time, 2)
                    if moving_time >= 1:  # filter out movements that are very short < 1s
                        self.moving_time += moving_time
                        self.transition_count += 1
                        if self.calibration:
                            self.moving_time_intervals.append(
                                [round(self.start_of_movement_time-self.start_of_program, 2),
                                 round(self.end_of_movement_time-self.start_of_program, 2)]
                            )
                self.is_moving = False
            self.moving_count = 0
            self.stationary_count = 0
            self.count = 0

    def get_end_of_movement_time(self):
        temp = None
        for i in range(len(self.dataset)):
            self.all_data[-len(self.dataset)+i].action_state = "IDLE"
            if self.dataset[i].speed > self.speed_threshold and temp:
                break
            temp = self.dataset[i].raw_time
        return temp

    def get_start_of_movement_time(self):
        temp = None
        for i in reversed(range(len(self.dataset))):
            self.all_data[-len(self.dataset)+i].is_moving = "MOVING"
            if self.dataset[i].speed < self.speed_threshold and temp:
                break
            temp = self.dataset[i].raw_time
        return temp

    def get_average_pos(self):
        sum_x = 0
        sum_y = 0
        for i in self.raw_data_buffer:
            sum_x += i.coordinates[0]
            sum_y += i.coordinates[1]
        return [sum_x / len(self.raw_data_buffer), sum_y / len(self.raw_data_buffer)]

    def reset(self):
        self.current_data_point = None
        self.raw_data_buffer = []
        self.dataset = []
        self.start_of_program = None
        self.count = 0
        self.moving_count = 0
        self.stationary_count = 0
        self.transition_count = 0
        self.moving_time = 0.0
        self.is_moving = False
        self.start_of_movement_time = None
        self.end_of_movement_time = None
        self.total_time_elapsed = None
        self.ready = False
        self.moving_time_intervals = []
        self.speeds = []
        self.timestamps = []
        self.all_data = []

