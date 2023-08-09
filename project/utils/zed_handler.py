"""
Handles processing and storing of Zed camera datasets
"""

import project.utils.inputs as inputs
from project.utils.directory_handler import DirectoryHandler

class ZedHandler(DirectoryHandler):
    def __init__(self):
        super(DirectoryHandler, self).__init__()
        self.zed_data = []
        self.filtered_data = []
        self.total_moving_time = 0.0
        self.UWB_start_time = None
        self.obj_id = None

    def get_zed_data(self):
        if self.datasets == "q":
            return "q"
        if not self.obj_id:
            self.obj_id = inputs.get_object_id()
        if self.obj_id == "q":
            return "q"

        for zed_dataset in self.datasets:
            zed_dataset.pop(0)
            for zed_data in zed_dataset:
                if (str(zed_data[0]) == self.obj_id or self.obj_id == "ANY") and str(zed_data[4] != "nan"):
                    zed_data_node = ZedData()
                    zed_data_node.set(float(zed_data[4]), float(zed_data[10]), zed_data[9])
                    self.zed_data.append(zed_data_node)

    def get_moving_time(self):
        is_moving = False
        start_time = None
        for data in self.filtered_data:
            if not is_moving and data.action_state == "MOVING":
                start_time = data.timestamp
                is_moving = True
            elif is_moving and data.action_state == "IDLE":
                end_time = data.timestamp
                is_moving = False
                if end_time-start_time >= 1:
                    moving_data = MovingData(round(start_time-self.UWB_start_time, 2), round(end_time-self.UWB_start_time, 2))
                    self.total_moving_time += round(moving_data.moving_time, 2)

    # Try to match timestamps between zed data and UWB data by taking the smallest difference between
    def match_timestamps(self, timestamp):
        return min(self.filtered_data, key=lambda obj: abs(timestamp - obj.timestamp))

    def filter_timestamps(self, start_time, end_time):
        self.UWB_start_time = start_time
        for i in self.zed_data:
            if start_time <= i.timestamp:
                self.filtered_data.append(i)
            elif end_time <= i.timestamp:
                break

    def reset(self):
        self.filtered_data = []
        self.total_moving_time = 0.0
        self.UWB_start_time = None

class ZedData:
    def __init__(self):
        self.velocity = None
        self.timestamp = None
        self.action_state = None

    def set(self, velocity, timestamp, action_state):
        self.velocity = velocity
        self.timestamp = timestamp
        self.action_state = action_state

class MovingData:
    def __init__(self, start_of_movement, end_of_movement):
        self.start_of_movement = start_of_movement
        self.end_of_movement = end_of_movement
        self.moving_time = self.end_of_movement-self.start_of_movement

