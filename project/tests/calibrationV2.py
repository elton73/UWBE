import os
import ast
import csv
import time
import project.utils.inputs as inputs
from project.experiment_tools.experiments import TagMovingV2 as TagMovingV2
from project.experiment_tools.tags import RawData as RawData
from project.utils.progress_bar import ProgressBar, find_common_settings
from config import TAG_ID

tag = TagMovingV2(TAG_ID)

def main():
    calibration_type = inputs.get_calibration_type(tag=tag)
    datasets, indexes = inputs.choose_csvs(tag=tag)
    time_start = time.perf_counter()

    if calibration_type == '1':
        generate_accuracy_table(datasets, indexes)
    elif calibration_type == '2':
        accuracy = inputs.get_max_error()
        generate_calibration_table(datasets, indexes, accuracy)
    elif calibration_type == '3':
        averaging_window = inputs.get_averaging_window()
        generate_speed_data(datasets, indexes, averaging_window)

    print(f"\nTime Taken: {(time.perf_counter() - time_start):.2f}")


def generate_accuracy_table(datasets, indexes):
    averaging_window_threshold_min = 3
    averaging_window_threshold_max = 35
    averaging_window_threshold_increment = 2
    averaging_window_threshold = averaging_window_threshold_min
    speed_threshold_min = 0.1
    speed_threshold_max = 1.0
    speed_threshold_increment = 0.1
    speed_threshold = speed_threshold_min
    count_min = 2
    count_max = 20
    count_increment = 2
    count = count_min
    save_data = True
    progress_bar = ProgressBar()
    progress_bar_max = float(len(indexes) * ((count_max - count + count_increment) / count_increment) *
                             (averaging_window_threshold_max - averaging_window_threshold +
                              averaging_window_threshold_increment) /
                             averaging_window_threshold_increment)
    progress_bar.set_max(progress_bar_max)

    for i, dataset in zip(indexes, datasets):
        calibration_complete = False
        dataset.pop(0)
        gold_standard_intervals = ast.literal_eval(dataset.pop()[0])
        gold_standard_time = float(dataset.pop()[0])
        gold_standard_transition_count = float(dataset.pop()[0])

        while not calibration_complete:
            tag.reset(f"Exp_{i}", i)
            tag.save_data = save_data
            tag.speed_threshold = speed_threshold
            tag.count_threshold = count
            tag.averaging_window_threshold = averaging_window_threshold
            tag.gold_standard_transition_count = gold_standard_transition_count
            tag.gold_standard_time = gold_standard_time
            tag.gold_standard_intervals = gold_standard_intervals

            for d in dataset:
                tag.add_data(RawData(ast.literal_eval(d[0]), d[1], float(d[2]), d[3]))

            tag.get_output()
            tag.write_csv()

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

    tag.close_csv()
    progress_bar.print_output()


def generate_calibration_table(datasets, indexes, max_error):
    averaging_window_threshold_min = 3
    averaging_window_threshold_max = 35
    averaging_window_threshold_increment = 2
    averaging_window_threshold = averaging_window_threshold_min
    speed_threshold_min = 0.1
    speed_threshold_max = 1.0
    speed_threshold_increment = 0.1
    speed_threshold = speed_threshold_min
    count_min = 2
    count_max = 20
    count_increment = 2
    count = count_min
    progress_bar = ProgressBar()
    progress_bar_max = float(len(indexes) * ((count_max - count + count_increment) / count_increment) *
                             (averaging_window_threshold_max - averaging_window_threshold +
                              averaging_window_threshold_increment) /
                             averaging_window_threshold_increment)
    progress_bar.set_max(progress_bar_max)
    settings = []

    for i, dataset in zip(indexes, datasets):
        dataset.pop(0)
        gold_standard_intervals = ast.literal_eval(dataset.pop()[0])
        gold_standard_time = float(dataset.pop()[0])
        gold_standard_transition_count = float(dataset.pop()[0])
        calibration_complete = False
        best_settings = []

        while not calibration_complete:
            tag.reset(f"Exp_{i}", i)
            tag.speed_threshold = speed_threshold
            tag.count_threshold = count
            tag.averaging_window_threshold = averaging_window_threshold
            tag.gold_standard_transition_count = gold_standard_transition_count
            tag.gold_standard_time = gold_standard_time
            tag.gold_standard_intervals = gold_standard_intervals

            for d in dataset:
                tag.add_data(RawData(ast.literal_eval(d[0]), d[1], float(d[2]), d[3]))

            tag.get_output()

            if not tag.find_error(max_error):
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

    tag.close_csv()
    progress_bar.print_output()
    common_settings = find_common_settings(settings)

    if len(common_settings) < 1:
        print("\nNo Common Settings! :( ")
        return

    path = os.path.join(os.getcwd(), "../../csv", tag.tag_id, "experiments", "moving_experiment", "ILS", "Calibrations")

    if not os.path.exists(path):
        os.makedirs(path)

    number = 1
    file_csv = os.path.join(path, f"calibration_{number}.csv")

    while os.path.exists(file_csv):
        number += 1
        file_csv = os.path.join(path, f"calibration_{number}.csv")

    with open(file_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([f"Max Error: {max_error}s"])
        writer.writerow(["speed_threshold", "count", "averaging_window_threshold"])

        for i in common_settings:
            writer.writerow(i)

    print(f"\n{len(common_settings)} common settings found!")


def generate_speed_data(datasets, indexes, averaging_window):
    save_speed = False

    for i, dataset in zip(indexes, datasets):
        dataset.pop(0)
        count = 3

        for k in range(count):
            dataset.pop()

        tag.reset(f"Exp_{i}", i)
        tag.averaging_window_threshold = averaging_window
        tag.save_speeds = save_speed
        tag.setup_speed_csv()

        for d in dataset:
            tag.add_data(RawData(ast.literal_eval(d[0]), d[1], float(d[2]), d[3]))

        tag.plot()
        tag.write_speed_csv()
        tag.close_csv()


if __name__ == '__main__':
    main()