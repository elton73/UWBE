from matplotlib import path
from collections import Counter

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