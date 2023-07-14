from project.utils.data import DataNode

class DataProcessorV2:
    def __init__(self):

        self.averaging_window_threshold = 10
        self.speed_threshold = 0.2
        self.count_threshold = 14

        self.index = self.averaging_window_threshold // 2
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

        self.raw_data = None
        self.buffer = []

    def add(self, raw_data):
        self.raw_data = raw_data

    def process(self):
        data = DataNode(a=self.raw_data.accelerometer, r=self.raw_data.raw_time, u=self.raw_data.update_rate)
        data.raw_coordinates = self.raw_data.coordinates
        self.buffer.append(data)
        if len(self.buffer) > self.averaging_window_threshold:
            data.coordinates = self.get_average_pos(self.buffer)
            if not self.start_of_program:
                self.start_of_program = data.raw_time
            if not self.dataset:
                self.dataset.append(data)
                if self.calibration:
                    self.speeds.append(data.speed)
                    self.timestamps.append(data.raw_time)
                return
            self.ready = True
            data.set_speed(self.dataset[-1])
            self.dataset.append(data)
            if self.calibration:
                self.speeds.append(data.speed)
                self.timestamps.append(data.raw_time)
            self.buffer = []
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
                    moving_time = self.end_of_movement_time - self.start_of_movement_time
                    if moving_time >= 1:  # filter out movements that are very short < 1s
                        self.moving_time += moving_time
                        self.transition_count += 1
                        if self.calibration:
                            self.moving_time_intervals.append([self.start_of_movement_time, self.end_of_movement_time])
                self.is_moving = False
            self.moving_count = 0
            self.stationary_count = 0
            self.count = 0

    def get_end_of_movement_time(self):
        for d in self.dataset:
            if d.speed < self.speed_threshold:
                # instead of using the timestamp of the speed, use the timestamp from the first coordinate to appear
                datapoint = next(i for i in self.dataset if i.raw_coordinates == d.raw_coordinates)
                return datapoint.raw_time

    def get_start_of_movement_time(self):
        for d in reversed(self.dataset):
            if d.speed > self.speed_threshold:
                return d.raw_time

    def get_average_pos(self, buffer):
        sum_x = 0
        sum_y = 0
        for i in buffer:
            sum_x += i.raw_coordinates[0]
            sum_y += i.raw_coordinates[1]
        return [sum_x / len(self.buffer), sum_y / len(self.buffer)]

    def reset(self):
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
        self.buffer = []
