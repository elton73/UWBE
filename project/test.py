class AlgorithmV2:
    def __init__(self, averaging_window_threshold, speed_threshold, count_threshold):

        self.averaging_window_threshold = averaging_window_threshold
        self.speed_threshold = speed_threshold
        self.count_threshold = count_threshold

        self.index = averaging_window_threshold // 2
        self.raw_data_buffer = []
        self.data_buffer = []

        self.start_of_program = None

        self.count = 0
        self.moving_count = 0
        self.stationary_count = 0
        self.transition_count = 0
        self.moving_time = 0.0
        self.is_moving = False
        self.start_of_movement_time = None
        self.end_of_movement_time = None

    def add(self, raw_data):
        self.raw_data_buffer.append(raw_data)

    def process(self):
        # fill data buffer with raw coordinates
        if len(self.raw_data_buffer) < self.averaging_window_threshold:
            return
        current_coordinate = self.raw_data_buffer[self.index]
        self.raw_data_buffer.pop(0)
        if not self.start_of_program:
            self.start_of_program = current_coordinate.raw_time

        #create a data object
        data = DataNodeV2(self.get_average_pos(), current_coordinate.accelerometer, current_coordinate.raw_time,
                          current_coordinate.update_rate)
        data.raw_coordinates = current_coordinate.coordinates

        #fill data buffer with averaged coordinates
        if len(self.data_buffer) < 1:
            self.data_buffer.append(data)
            return

        # get the speed from averaged coordinates
        data.set_speed(self.data_buffer[-1])
        self.data_buffer.append(data)
        if len(self.data_buffer) > self.count_threshold:
            self.data_buffer.pop(0)

        self.evaluate_data()

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
            else:
                if self.is_moving:
                    self.end_of_movement_time = self.get_end_of_movement_time()
                    moving_time = self.end_of_movement_time - self.start_of_movement_time
                    if moving_time >= 0.5: # filter out movements that are very short <0.5s
                        self.moving_time += moving_time
                        self.transition_count += 1
                self.is_moving = False
            self.moving_count = 0
            self.stationary_count = 0
            self.count = 0

    def get_end_of_movement_time(self):
        for d in self.data_buffer:
            if d.speed < self.speed_threshold:
                # instead of using the timestamp of the speed, use the timestamp from the first coordinate to appear
                datapoint = next(i for i in self.data_buffer if i.raw_coordinates == d.raw_coordinates)
                return datapoint.raw_time

    def get_start_of_movement_time(self):
        for d in reversed(self.data_buffer):
            if d.speed > self.speed_threshold:
                return d.raw_time



    def get_average_pos(self):
        sum_x = 0
        sum_y = 0
        for i in self.raw_data_buffer:
            sum_x += i.x
            sum_y += i.y
        return [sum_x / len(self.raw_data_buffer), sum_y / len(self.raw_data_buffer)]
