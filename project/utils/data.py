"""
Data classes for tracking all data #incomplete
"""

import datetime
import math


class DataNodeV2:
    def __init__(self, c, a, r, u):
        self.coordinates = c
        self.x = c[0]
        self.y = c[1]
        self.accelerometer = a
        self.raw_time = r
        self.update_rate = u
        self.speed = 0.0
        self.index = None
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


class DataNodeV7:
    def __init__(self, coordinates, index, raw_time, speed=0.0):
        self.coordinates = coordinates
        self.speed = speed
        self.index = index
        self.is_moving = False
        self.raw_time = raw_time
