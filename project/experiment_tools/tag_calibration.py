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

        self.furniture_detection_experiment = False

        self.csv_data = []

    def add_data(self, data):
        try:
            accelerometer = data['data']['tagData']['accelerometer'][0]
        except:
            accelerometer = []
        self.coordinates = [data['data']['coordinates']['x'], data['data']['coordinates']['y']]
        self.zone.get(self.coordinates)
        raw_time = data['timestamp']
        update_rate = data['data']['metrics']['rates']['update']
        if not self.furniture_detection_experiment:
            self.csv_data = [
                self.coordinates,
                accelerometer,
                raw_time,
                update_rate,
                self.zone.name
                ]
        else:
            self.csv_data = [
                raw_time,
                self.coordinates[0],
                self.coordinates[1]
            ]

