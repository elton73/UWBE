# Generate an accuracy table (csv with all accuracies for different settings),
# generate a calibration table (csv with all settings that hold within a certain accuracy for multiple experiments)
# generate a speed plot
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

matplotlib.rcParams['interactive'] == True
tag = TagAnalyzer(TAG_ID, data_processor="1")
tag.activate_calibration_mode()
zed_handler = ZedHandler()

# settings for speed table
save_speed = False # Toggle if you want to save speed data
compare_with_zed = True # Toggle to overlay graphs with zed data
smooth_data = True # Toggle to apply a smoothing function

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

dir_handler = DirectoryHandler()

def main():
    # choose output type
    user_input = inputs.get_calibration_type()
    if user_input == "q":
        return
    calibration_type = user_input

    if calibration_type == "2":
        max_error = inputs.get_target_accuracy()
        if max_error == "q":
            return

    if calibration_type != "3":
        # get csvs
        print("Choose UWB CSVs")
        user_input = dir_handler.choose_csvs()
        if user_input == "q":
            return
    else:
        # get single csv
        print("Choose a UWB CSV")
        user_input = dir_handler.choose_single_csv()
        if user_input == "q":
            return
    datasets = dir_handler.read_csvs()

    if compare_with_zed or calibration_type == "2" or calibration_type == "1":
        print("Choose a Zed CSV To Compare")
        if zed_handler.choose_single_csv() == "q":
            return
        data = zed_handler.get_zed_data()
        if data == "q":
            return

    # get output directory unless user just wants to plot speed
    if save_speed or calibration_type != "3":
        print("Choose where files should be saved")
        user_input = dir_handler.choose_output_directory()
        if user_input == "q":
            return

    time_start = time.perf_counter()

    if calibration_type == '1':
        generate_accuracy_table(datasets)
    elif calibration_type == '2':
        generate_calibration_table(datasets, max_error)
    elif calibration_type == '3':
        generate_speed_data(datasets)

    print(f"\nTime Taken: {(time.perf_counter() - time_start):.2f}")


def generate_accuracy_table(datasets):
    dir_handler.setup_csv("accuracy_table")
    averaging_window_threshold = averaging_window_threshold_min
    speed_threshold = speed_threshold_min
    count = count_min

    # setup progress bar
    progress_bar = ProgressBar()
    progress_bar_max = float(len(datasets) * ((count_max - count + count_increment) / count_increment) *
                             (averaging_window_threshold_max - averaging_window_threshold +
                              averaging_window_threshold_increment) /
                             averaging_window_threshold_increment)
    progress_bar.set_max(progress_bar_max)

    for dataset in datasets:
        calibration_complete = False
        exp_description = dataset[0][0]
        dataset.pop(0)
        dir_handler.write_csv(tag.csv_data_names)
        sorted_dataset = sorted(dataset, key=lambda sublist: sublist[2])

        while not calibration_complete:
            tag.exp_description = exp_description
            tag.data_processor.reset()
            zed_handler.reset()

            tag.data_processor.speed_threshold = speed_threshold
            tag.data_processor.count_threshold = count
            tag.data_processor.averaging_window_threshold = averaging_window_threshold
            tag.data_processor.index = averaging_window_threshold // 2

            for d in sorted_dataset:
                tag.add_data(RawData(ast.literal_eval(d[0]), d[1], float(d[2]), d[3]))

            zed_handler.filter_timestamps(tag.data_processor.start_of_program, tag.data_processor.dataset[-1].raw_time)
            zed_handler.get_movement_intervals()

            tag.gold_standard_time = zed_handler.total_moving_time
            tag.gold_standard_intervals = zed_handler.movement_intervals
            tag.gold_standard_transitions = zed_handler.transitions

            tag.get_output()
            dir_handler.write_csv(tag.csv_data)

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


def generate_calibration_table(datasets, accuracy):
    averaging_window_threshold = averaging_window_threshold_min
    speed_threshold = speed_threshold_min
    count = count_min

    #setup progress bar
    progress_bar = ProgressBar()
    progress_bar_max = float(len(datasets) * ((count_max - count + count_increment) / count_increment) *
                             (averaging_window_threshold_max - averaging_window_threshold +
                              averaging_window_threshold_increment) /
                             averaging_window_threshold_increment)
    progress_bar.set_max(progress_bar_max)

    settings = []
    for dataset in datasets:
        calibration_complete = False
        exp_description = dataset[0][0]
        dataset.pop(0)
        dir_handler.write_csv(tag.csv_data_names)
        sorted_dataset = sorted(dataset, key=lambda sublist: sublist[2])

        best_settings = []
        while not calibration_complete:
            tag.exp_description = exp_description
            tag.data_processor.reset()
            zed_handler.reset()

            tag.data_processor.speed_threshold = speed_threshold
            tag.data_processor.count_threshold = count
            tag.data_processor.averaging_window_threshold = averaging_window_threshold
            tag.data_processor.index = averaging_window_threshold // 2

            for d in sorted_dataset:
                tag.add_data(RawData(ast.literal_eval(d[0]), d[1], float(d[2]), d[3]))

            zed_handler.filter_timestamps(tag.data_processor.start_of_program, tag.data_processor.dataset[-1].raw_time)
            zed_handler.get_movement_intervals()

            tag.gold_standard_time = zed_handler.total_moving_time
            tag.gold_standard_intervals = zed_handler.movement_intervals
            tag.gold_standard_transitions = zed_handler.transitions

            tag.get_output()
            if tag.accuracy <= accuracy:
                best_settings.append((speed_threshold, count, averaging_window_threshold))

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

    dir_handler.setup_csv("calibration_table")
    dir_handler.write_csv([f"Target Accuracy: {accuracy}s"])
    dir_handler.write_csv(["speed_threshold", "count", "averaging_window_threshold"])
    for i in common_settings:
        dir_handler.write_csv(i)
    dir_handler.close_csvs()
    print(f"\n{len(common_settings)} common settings found!")

def generate_speed_data(datasets):
    dataset = datasets[0]
    if save_speed:
        tag.speed_format()

    # Set window sizes to plot
    averaging_windows = []
    averaging_window_threshold = averaging_window_threshold_min
    while averaging_window_threshold <= averaging_window_threshold_max:
        averaging_windows.append(averaging_window_threshold)
        averaging_window_threshold += averaging_window_threshold_increment

    # remove unnecessary rows in the csv
    exp_description = dataset[0][0]
    dataset.pop(0)
    sorted_dataset = sorted(dataset, key=lambda sublist: sublist[2])

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

        if compare_with_zed:
            zed_handler.filter_timestamps(tag.data_processor.timestamps[0], tag.data_processor.timestamps[1])
            timestamps = []
            velocities = []
            for data in zed_handler.filtered_data:
                timestamps.append(data.timestamp)
                velocities.append(data.velocity)
            plt.plot(timestamps, velocities, label="Zed")
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

def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

if __name__ == '__main__':
    main()

# C:\Users\ML-2\Documents\GitHub\UWBE\venv\Scripts\python C:\Users\ML-2\Documents\GitHub\UWBE\calibrationV2.py