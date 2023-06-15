import numpy as np
from scipy.interpolate import CubicSpline
import project.utils.inputs as inputs
import ast
import math

def main():
    arr = []
    x = []
    y = []
    timestamp = []
    datasets, indexes = inputs.choose_csvs()
    for dataset in datasets:
        dataset = dataset[1:-3]
        for d in dataset:
            x.append(ast.literal_eval(d[0])[0])
            y.append(ast.literal_eval(d[0])[1])
            timestamp.append(float(d[2]))
    print(calculate_movement_time(x, y, timestamp))



def calculate_movement_time(x_coords, y_coords, timestamps):
    total_distance = 0
    total_time = timestamps[-1] - timestamps[0]  # Total time elapsed

    for i in range(1, len(x_coords)):
        current_x = x_coords[i]
        current_y = y_coords[i]
        previous_x = x_coords[i-1]
        previous_y = y_coords[i-1]

        distance = math.sqrt((current_x - previous_x) ** 2 + (current_y - previous_y) ** 2)
        total_distance += distance

    if total_time == 0:
        return 0

    average_speed = total_distance / total_time
    movement_time = total_distance / average_speed

    return movement_time





if __name__ == '__main__':
    main()