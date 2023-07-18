"""
Plot coordinates
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
    print("Choose an Accuracy Table")
    user_input = dir_handler.choose_single_csv()
    if user_input == "q":
        return

    datasets = dir_handler.read_csvs()

    # get output directory to save plot
    if save:
        print("Choose where files should be saved")
        dir_handler.choose_output_directory()
        user_input = dir_handler.choose_output_directory()
        if user_input == "q":
            return

    plot(datasets, calibration_plot_type)

### remove later
# count = d[9]
# speed_threshold = d[10]
# averaging_window = d[11]
def plot(datasets, type):
    for dataset in datasets:
        dataset.pop(0)
        calibration_counter = defaultdict(int)

        for d in dataset:
            accuracy = d[2]
            if type == "1":
                setting = d[9]
            elif type == "2":
                setting = d[10]
            elif type == "3":
                setting = d[11]
            if float(accuracy) > 0.9:
                calibration_counter[setting] += 1

        sorted_keys = sorted(calibration_counter.keys(), key=lambda x: int(x))
        print(sorted_keys)
        y = []
        for key in sorted_keys:
            y.append(calibration_counter[key])  # store number of rows with accuracy greater than 90

        plt.scatter(sorted_keys, y, s=5)
        plt.show()

if __name__ == '__main__':
    main()
