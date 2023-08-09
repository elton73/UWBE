"""
Generate an accuracy table (csv with all accuracies for different settings),
generate a calibration table (csv with all settings that hold within a certain accuracy for multiple experiments)
generate a speed plot
"""

import ast
import time
import project.utils.inputs as inputs
from project.experiment_tools.tag_analyze import TagAnalyzer
from project.utils.data import RawData as RawData
from project.utils.progress_bar import ProgressBar, find_common_settings
from config import TAG_ID
import matplotlib
from matplotlib import pyplot as plt
from project.utils.directory_handler import DirectoryHandler
from project.utils.zed_handler import ZedHandler
import numpy as np
import os
import winsound

"""
Important Globals
"""
tag = TagAnalyzer(TAG_ID, data_processor="1")  # choose data processor to use from experiment_tools

# settings for speed table
save_speed = False # Toggle if you want to save speed data
compare_with_zed = True # Toggle to overlay graphs with zed data
smooth_data = False # Toggle to apply a smoothing function

# calibration settings to test
averaging_window_threshold_min = 3
averaging_window_threshold_max = 71
averaging_window_threshold_increment = 2
speed_threshold_min = 0.1
speed_threshold_max = 2.0
speed_threshold_increment = 0.05
count_min = 2
count_max = 40
count_increment = 2

# #quick debug
# averaging_window_threshold_min = 3
# averaging_window_threshold_max = 7
# averaging_window_threshold_increment = 2
# speed_threshold_min = 0.1
# speed_threshold_max = 0.3
# speed_threshold_increment = 0.05
# count_min = 2
# count_max = 6
# count_increment = 2

# initialize some settings (don't change these)
matplotlib.rcParams['interactive'] = True
tag.activate_calibration_mode()
zed_handler = ZedHandler()
dir_handler = DirectoryHandler()

# Ask user for calibration type and get the input and output csv directories.
def main():
    # ask user for output type and end program if user enters q
    user_input = inputs.get_calibration_type()
    if user_input == "q":
        return
    calibration_type = user_input
    # if user is making a calibration table, ask them for the target accuracy
    if calibration_type == "2":
        max_error = inputs.get_target_accuracy()
        if max_error == "q":
            return

    # ask user to select UWB csv files and end program if user selects nothing
    print("Choose UWB CSVs")
    user_input = dir_handler.choose_csvs()
    if user_input == "q":
        return

    # This is strictly for plotting. If compare_with_zed is on, the plot will only show UWB data.
    if compare_with_zed or calibration_type == "2" or calibration_type == "1":
        print("Choose Zed CSVs To Compare")
        if zed_handler.choose_csvs() == "q":
            return

    # get output directory unless user only wants to plot speed
    if save_speed or calibration_type != "3":
        print("Choose where files should be saved")
        user_input = dir_handler.choose_output_directory()
        if user_input == "q":
            return

    time_start = time.perf_counter()

    if calibration_type == '1':
        generate_accuracy_table()
    elif calibration_type == '2':
        generate_calibration_table(max_error)
    elif calibration_type == '3':
        generate_speed_data()

    print(f"\nTime Taken: {(time.perf_counter() - time_start):.2f}")


# A table showing the accuracies for different combinations of count, speed_threshold, and averaging windows
def generate_accuracy_table():
    # set smallest values for calibration settings
    averaging_window_threshold = averaging_window_threshold_min
    speed_threshold = speed_threshold_min
    count = count_min

    # iterate through each selected csv file the user chose previously
    for uwb_path in dir_handler.file_paths:
        uwb_file_name = os.path.basename(uwb_path)
        # Here we match up the UWB csv file and the Zed csv file by name. If the program cannot find matching files,
        # then there is no gold standard to compare and the program will end.
        if zed_handler.read_csvs(file_name=uwb_file_name) == "q" or dir_handler.read_csvs(file_name=uwb_file_name):
            return
        # Once the correct csv is found, we extract the data and prep it for comparison later
        zed_handler.get_zed_data()
        print(f"Analyzing dataset: {uwb_file_name}") # This is just to track which file the program is currently working on
        # setup progress bar
        progress_bar = ProgressBar()
        progress_bar_max = float(len(dir_handler.file_paths) * ((count_max - count + count_increment) / count_increment) *
                                 (averaging_window_threshold_max - averaging_window_threshold +
                                  averaging_window_threshold_increment) /
                                 averaging_window_threshold_increment)
        progress_bar.set_max(progress_bar_max)

        # create the output csv in the output directory chosen previously. It will have the name accuracy_table
        # followed by a number
        dir_handler.setup_csv("accuracy_table")
        dataset = dir_handler.datasets[0]  # Grab the csv dataset
        calibration_complete = False
        # the first row of the csv will have the experiment title. Grab it and then pop the row
        exp_description = dataset[0][0]
        dataset.pop(0)
        # write the column names into the output csv
        dir_handler.write_csv(tag.csv_data_names)
        # Sometimes, the UWB system messes up the order of datapoints so we sort the dataset by timestamp just in case.
        sorted_dataset = sorted(dataset, key=lambda sublist: sublist[2])

        # Iterate through every combination of calibrations and print the results into the csv
        while not calibration_complete:
            tag.exp_description = exp_description

            # After running a calibration, reset all objects in preparation for the next calibration
            tag.data_processor.reset()
            zed_handler.reset()

            # set the object with new calibrations
            tag.data_processor.speed_threshold = speed_threshold
            tag.data_processor.count_threshold = count
            tag.data_processor.averaging_window_threshold = averaging_window_threshold
            tag.data_processor.index = averaging_window_threshold // 2

            # Process the UWB data as if the data is coming in live
            for d in sorted_dataset:
                tag.add_data(RawData(ast.literal_eval(d[0]), d[1], float(d[2]), d[3]))

            # remove all datapoints from the zed dataset that happens before or after the UWB dataset
            zed_handler.filter_timestamps(tag.data_processor.start_of_program, tag.data_processor.dataset[-1].raw_time)
            zed_handler.get_moving_time()

            # Use a confusion matrix to compare the UWB data to Zed data
            tag.get_output(zed_handler)

            # Write the final results to the csv
            dir_handler.write_csv(tag.csv_data)

            # Increment the calibration settings until all combinations are completed
            speed_threshold += speed_threshold_increment
            if speed_threshold > speed_threshold_max:
                speed_threshold = speed_threshold_min
                count += count_increment
                progress_bar.update_bar()
                progress_bar.print_output()
            if count > count_max:
                count = count_min
                averaging_window_threshold += averaging_window_threshold_increment
            if averaging_window_threshold > averaging_window_threshold_max:
                calibration_complete = True
                averaging_window_threshold = averaging_window_threshold_min
                speed_threshold = speed_threshold_min
                count = count_min

        dir_handler.close_csvs()
        progress_bar.print_output()
    winsound.Beep(440, 500)  # beep when the program is finished


# Generate a list of all combinations of calibration settings that return an accuracy over the target accuracy
def generate_calibration_table(accuracy):
    # set smallest values for calibration settings
    averaging_window_threshold = averaging_window_threshold_min
    speed_threshold = speed_threshold_min
    count = count_min

    settings = []  # list of all settings that return an accuracy above target accuracy for all experiments

    # iterate through each selected csv file the user chose previously
    for uwb_path in dir_handler.file_paths:
        uwb_file_name = os.path.basename(uwb_path)
        # Here we match up the UWB csv file and the Zed csv file by name. If the program cannot find matching files,
        # then there is no gold standard to compare and the program will end.
        if zed_handler.read_csvs(file_name=uwb_file_name) == "q" or dir_handler.read_csvs(file_name=uwb_file_name):
            return
        # Once the correct csv is found, we extract the data and prep it for comparison later
        zed_handler.get_zed_data()
        print(f"Analyzing dataset: {uwb_file_name}")  # This is just to track which file the program is currently working on
        # setup progress bar
        progress_bar = ProgressBar()
        progress_bar_max = float(
            len(dir_handler.file_paths) * ((count_max - count + count_increment) / count_increment) *
            (averaging_window_threshold_max - averaging_window_threshold +
             averaging_window_threshold_increment) /
            averaging_window_threshold_increment)
        progress_bar.set_max(progress_bar_max)
        print(f"Analyzing dataset: {uwb_file_name}")

        dataset = dir_handler.datasets[0]  # Grab the csv dataset
        calibration_complete = False

        # the first row of the csv will have the experiment title. Grab it and then pop the row
        exp_description = dataset[0][0]
        dataset.pop(0)
        # Sometimes, the UWB system messes up the order of datapoints so we sort the dataset by timestamp just in case.
        sorted_dataset = sorted(dataset, key=lambda sublist: sublist[2])
        best_settings = []
        while not calibration_complete:
            tag.exp_description = exp_description

            # After running a calibration, reset all objects in preparation for the next calibration
            tag.data_processor.reset()
            zed_handler.reset()

            # set the object with new calibrations
            tag.data_processor.speed_threshold = speed_threshold
            tag.data_processor.count_threshold = count
            tag.data_processor.averaging_window_threshold = averaging_window_threshold
            tag.data_processor.index = averaging_window_threshold // 2

            # Process the UWB data as if the data is coming in live
            for d in sorted_dataset:
                tag.add_data(RawData(ast.literal_eval(d[0]), d[1], float(d[2]), d[3]))

            # remove all datapoints from the zed dataset that happens before or after the UWB dataset
            zed_handler.filter_timestamps(tag.data_processor.start_of_program, tag.data_processor.dataset[-1].raw_time)
            zed_handler.get_moving_time()

            # Use a confusion matrix to compare the UWB data to Zed data
            tag.get_output(zed_handler)

            # check the accuracy of the current calibration, if it is above the target accuracy, add it to the list of best settings
            if tag.accuracy >= accuracy:
                best_settings.append((speed_threshold, count, averaging_window_threshold))

            # Increment the calibration settings until all combinations are completed
            speed_threshold += speed_threshold_increment
            if speed_threshold > speed_threshold_max:
                speed_threshold = speed_threshold_min
                count += count_increment
                progress_bar.update_bar()
                progress_bar.print_output()

            if count > count_max:
                count = count_min
                averaging_window_threshold += averaging_window_threshold_increment

            if averaging_window_threshold > averaging_window_threshold_max:
                calibration_complete = True
                settings.append(best_settings)
                averaging_window_threshold = averaging_window_threshold_min
                speed_threshold = speed_threshold_min
                count = count_min
        # break the loop if no settings are found
        if settings == [] or len(find_common_settings(settings)) < 1:
            break

    progress_bar.print_output()

    common_settings = find_common_settings(settings)
    if len(common_settings) < 1:
        print("\nNo Common Settings! :( ")
        return

    # if common calibration settings are found, write them to a csv named calibration_table
    dir_handler.setup_csv("calibration_table")
    dir_handler.write_csv([f"Target Accuracy: {accuracy}s"])
    dir_handler.write_csv(["speed_threshold", "count", "averaging_window_threshold"])
    for i in common_settings:
        dir_handler.write_csv(i)
    dir_handler.close_csvs()
    print(f"\n{len(common_settings)} common settings found!")
    winsound.Beep(440, 500)  # beep when the program is finished

# Plots the speed vs time graph of the UWB and the Zed camera datasets
def generate_speed_data():
    dataset = dir_handler.datasets[0]  # grab the UWB data
    if save_speed: # if save_speed is on, prep a csv to be written to
        tag.speed_format()

    # Set different averaging window sizes to plot
    averaging_windows = []
    averaging_window_threshold = averaging_window_threshold_min
    while averaging_window_threshold <= averaging_window_threshold_max:
        averaging_windows.append(averaging_window_threshold)
        averaging_window_threshold += averaging_window_threshold_increment

    # remove experiment title row in the csv
    exp_description = dataset[0][0]
    dataset.pop(0)
    sorted_dataset = sorted(dataset, key=lambda sublist: sublist[2])

    # iterate through each averaging window and plot how the data looks
    for averaging_window in averaging_windows:
        if save_speed:
            dir_handler.setup_csv("speed_data")
            dir_handler.write_csv(tag.csv_data_names)
        tag.exp_description = exp_description
        tag.data_processor.reset()
        tag.data_processor.averaging_window_threshold = averaging_window
        tag.data_processor.index = averaging_window // 2
        for d in sorted_dataset:
            try:
                tag.add_data(RawData(ast.literal_eval(d[0]), d[1], float(d[2]), d[3]))
                if save_speed and tag.data_processor.ready:
                    dir_handler.write_csv(tag.csv_data)
            except Exception as e:
                print(e)
                print("Process Failed. Please check that CSV files were correct.")
                return
        # plot the zed data on top of the UWB data
        if compare_with_zed:
            zed_handler.filter_timestamps(tag.data_processor.timestamps[0], tag.data_processor.timestamps[1])
            timestamps = []
            velocities = []
            for data in zed_handler.filtered_data:
                timestamps.append(data.timestamp)
                velocities.append(data.velocity)
            plt.plot(timestamps, velocities, label="Zed")
            # apply a smoothing function to the UWB data
            if smooth_data:
                plt.plot(tag.data_processor.timestamps, smooth(tag.data_processor.speeds, 13), label="UWB")
            else:
                plt.plot(tag.data_processor.timestamps, tag.data_processor.speeds, label="UWB")
            plt.legend()
            plt.title(f"Averaging Window: {averaging_window}")
            plt.show()
        else:
            plt.plot(tag.data_processor.timestamps, tag.data_processor.speeds)
            plt.title(f"Averaging Window: {averaging_window}")
            plt.show()
        dir_handler.close_csvs()

# smoothing function for smoothing speed datasets
def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

if __name__ == '__main__':
    main()

# C:\Users\ML-2\Documents\GitHub\UWBE\venv\Scripts\python C:\Users\ML-2\Documents\GitHub\UWBE\calibrationV2.py