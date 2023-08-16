"""
Plot accuracy table results
"""
import matplotlib
from collections import defaultdict
from matplotlib import pyplot as plt
from project.utils.directory_handler import DirectoryHandler
import project.utils.inputs as inputs

matplotlib.rcParams['interactive'] = True
dir_handler = DirectoryHandler()

save = False

def main():
    # choose output type
    user_input = inputs.get_calibration_plot_type()
    if user_input == "q":
        return
    calibration_plot_type = user_input

    # get single csv
    print("Choose Accuracy Tables")
    user_input = dir_handler.choose_csvs()
    if user_input == "q":
        return

    dir_handler.read_csvs()

    # get output directory to save plot
    if save:
        print("Choose where files should be saved")
        dir_handler.choose_output_directory()
        user_input = dir_handler.choose_output_directory()
        if user_input == "q":
            return

    plot(calibration_plot_type)

def plot(type):
    for dataset in dir_handler.datasets:
        dataset.pop(0)
        calibration_counter = defaultdict(int)

        for d in dataset:
            accuracy = d[2]
            if type == "1":
                setting = d[10]
            elif type == "2":
                setting = d[11]
            elif type == "3":
                setting = d[12]
            if float(accuracy) > 0.85:
                calibration_counter[setting] += 1

        sorted_keys = sorted(calibration_counter.keys(), key=lambda x: float(x))
        y = []
        for key in sorted_keys:
            y.append(calibration_counter[key])  # store number of rows with accuracy greater than 90

        plt.scatter([round(float(key), 2) for key in sorted_keys], y, s=5)
        plt.xticks(rotation='vertical')
        plt.show()

if __name__ == '__main__':
    main()
