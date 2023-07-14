import project.utils.inputs as inputs
from project.utils.directory_handler import DirectoryHandler

class ZedHandler(DirectoryHandler):
    def __init__(self):
        super(DirectoryHandler, self).__init__()
        self.zed_data = []
        self.filtered_data = []
        self.movement_intervals = []
        self.total_moving_time = 0.0
        self.transitions = 0
        self.UWB_start_time = None

    def get_zed_data(self):
        zed_datasets = self.read_csvs()
        if zed_datasets == "q":
            return "q"
        obj_id = inputs.get_object_id()
        if obj_id == "q":
            return "q"

        zed_dataset = zed_datasets[0]
        zed_dataset.pop(0)
        for zed_data in zed_dataset:
            if str(zed_data[0]) == obj_id and str(zed_data[4] != "nan"):
                zed_data_node = ZedData()
                zed_data_node.set(float(zed_data[4]), float(zed_data[10]), zed_data[9])
                self.zed_data.append(zed_data_node)

    def get_movement_intervals(self):
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
                    self.transitions += 1
                    moving_data = MovingData(round(start_time-self.UWB_start_time, 2), round(end_time-self.UWB_start_time, 2))
                    self.movement_intervals.append([moving_data.start_of_movement, moving_data.end_of_movement])
                    self.total_moving_time += round(moving_data.moving_time, 2)

    def filter_timestamps(self, start_time, end_time):
        self.UWB_start_time = start_time
        self.filtered_data = []
        for i in self.zed_data:
            if start_time <= i.timestamp:
                self.filtered_data.append(i)
            elif end_time <= i.timestamp:
                break

    def reset(self):
        self.movement_intervals = []
        self.total_moving_time = 0.0
        self.transitions = 0

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

