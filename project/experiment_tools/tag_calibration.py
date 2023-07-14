"""
Class for retrieving a raw dataset for calibration
"""
from project.utils.accuracy import Accuracy
from project.experiment_tools.zones import Zone

# Modified version of Tag class for a calibration experiment
class TagCalibration(Accuracy):
    def __init__(self, tag_id):
        super(Accuracy, self).__init__()
        self.tag_id = tag_id

        self.comments = None
        self.gold_standard_time = None
        self.gold_standard_transition_count = 0
        self.gold_standard_intervals = []
        self.coordinates = None
        self.zone = Zone()

    def add_data(self, data):
        try:
            accelerometer = data['data']['tagData']['accelerometer'][0]
        except:
            return
        self.coordinates = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        self.zone.get(self.coordinates)
        raw_time = data['timestamp']
        update_rate = data['data']['metrics']['rates']['update']
        raw_data = [self.coordinates, accelerometer, raw_time, update_rate, self.zone.name]

