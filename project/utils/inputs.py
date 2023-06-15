import os
import csv
from config import TAG_ID

def get_tag_id():
    user_input = input("Enter tag id: ")
    if user_input == "q":
        raise SystemExit
    return user_input
def get_experiment_description(tag=None):
    user_input = input("Enter Experiment Description: ")
    if user_input == "q":
        if tag:
            tag.close_csv()
        raise SystemExit
    return user_input

def get_route_number(tag=None):
    user_input = input("Enter Route Number: ")
    if user_input == "q":
        if tag:
            tag.close_csv()
        raise SystemExit
    return user_input

def get_moving_time(tag=None):
    intervals = []
    for t in range(int(tag.gold_standard_transition_count)):
        input_flag = True
        while input_flag:
            user_input = input("Enter Moving Time: ")
            if user_input == "q":
                raise SystemExit
            else:
                try:
                    moving_time = float(user_input)
                    intervals.append(moving_time)
                    input_flag = False
                except ValueError:
                    print("Invalid Input. Please Try Again!")
    return intervals

def get_transition_count(tag=None):
    while 1:
        user_input = input("Enter Number Of Transitions: ")
        if user_input == "q":
            if tag:
                tag.close_csv()
            raise SystemExit
        elif not user_input.isnumeric():
            print("Invalid Input. Please Try Again!")
        else:
            return user_input

def choose_csvs(tag=None):
    datasets = []
    indexes = []
    print("Enter s to begin or q to quit")
    while 1:
        counter = str(input("Enter an experiment number: "))
        if "q" in counter:  # quit calibration
            if tag:
                tag.close_csv()
            raise SystemExit
        elif "s" in counter:  # begin calibration
            if len(datasets) > 0:
                return datasets, indexes
            else:
                print("No data!")
        elif counter.isnumeric() and counter not in indexes:
            path = os.path.join(os.getcwd(),
                                "../../",
                                "csv",
                                TAG_ID,
                                "experiments",
                                "moving_experiment",
                                "ILS",
                                "raw_data",
                                f"Exp_{counter}.csv")
            if not os.path.exists(path):
                print(path)
                print("No such experiment! Please Try Again")
            else:
                file = open(path, "r")
                data = list(csv.reader(file, delimiter=","))
                file.close()
                datasets.append(data)
                indexes.append(counter)
        else:
            print("Invalid Input. Please Try Again")

def get_calibration_type(tag=None):
    print("Enter Calibration Type Here! 1. Generate Accuracy Table; 2. Generate Calibration Table; 3. Generate Speed Table And Plot")
    while 1:
        user_input = input("Enter Calibration Type: ")
        if user_input == "q":
            if tag:
                tag.close_csv()
            raise SystemExit
        elif user_input == '1' or user_input == '2' or user_input == '3':
            return user_input
        else:
            print("Invalid Input. Please Try Again!")
def get_accuracy(tag = None):
    while 1:
        user_input = input("Enter Target Accuracy (Decimal): ")
        if user_input == "q":
            if tag:
                tag.close_csv()
            raise SystemExit
        else:
            try:
                accuracy = float(user_input)
                if 0 <= accuracy <= 1.0:
                    return accuracy
            except ValueError:
                pass
            print("Invalid Input. Please Try Again!")

def get_max_error(tag = None):
    while 1:
        user_input = input("Enter Max Error (Seconds): ")
        if user_input == "q":
            if tag:
                tag.close_csv()
            raise SystemExit
        else:
            try:
                accuracy = float(user_input)
                return accuracy
            except ValueError:
                print("Invalid Input. Please Try Again!")

def get_averaging_window(tag = None):
    while 1:
        user_input = input("Enter Averaging Window (Odd Number): ")
        if user_input == "q":
            if tag:
                tag.close_csv()
            raise SystemExit
        elif user_input.isnumeric() and int(user_input) % 2 != 0:
            return int(user_input)
        else:
            print("Invalid Input. Please Try Again!")
