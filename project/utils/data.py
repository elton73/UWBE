"""
Data classes for tracking all data
"""

import math


class DataNode:
    def __init__(self, c=None, a=None, r=None, u=None):
        self.coordinates = c
        self.accelerometer = a
        self.raw_time = r
        self.update_rate = u
        self.speed = 0.0
        self.index = None
        self.action_state = "IDLE"
        self.raw_coordinates = None

    def set_speed(self, data):
        distance = float(math.dist(data.coordinates, self.coordinates)) / 1000.0
        timeframe = self.raw_time - data.raw_time
        self.speed = float(distance / timeframe)


class RawData:
    def __init__(self, c, a, r, u):
        self.coordinates = c
        self.x = c[0]
        self.y = c[1]
        self.accelerometer = a
        self.raw_time = r
        self.update_rate = u

