import os
import csv
from config import TAG_ID

def get_tag_id():
    user_input = input("Enter tag id: ")
    if user_input == "q":
        return "q"
    return user_input
def get_experiment_description():
    user_input = input("Enter Experiment Description: ")
    if user_input == "q":
        return "q"
    return user_input

def get_route_number():
    user_input = input("Enter Route Number: ")
    if user_input == "q":
        return "q"
    return user_input

def get_moving_time(tag):
    intervals = []
    for t in range(int(tag.gold_standard_transition_count)):
        input_flag = True
        while input_flag:
            user_input = input("Enter Moving Time: ")
            if user_input == "q":
                return "q"
            else:
                try:
                    moving_time = float(user_input)
                    intervals.append(moving_time)
                    input_flag = False
                except ValueError:
                    print("Invalid Input. Please Try Again!")
    return intervals

def get_transition_count():
    while 1:
        user_input = input("Enter Number Of Transitions: ")
        if user_input.isnumeric() or user_input == "q":
            return user_input
        else:
            print("Invalid Input. Please Try Again!")

def choose_csvs():
    datasets = []
    indexes = []
    print("Enter s to begin or q to quit")
    while 1:
        counter = str(input("Enter an experiment number: "))
        if "q" in counter:  # quit calibration
            return "q"
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

def get_calibration_type():
    print("Enter Calibration Type Here! 1. Generate Accuracy Table; 2. Generate Calibration Table; 3. Generate Speed Table And Plot")
    while 1:
        user_input = input("Enter Calibration Type: ")
        if user_input == '1' or user_input == '2' or user_input == '3' or user_input == "q":
            return user_input
        else:
            print("Invalid Input. Please Try Again!")
def get_accuracy():
    while 1:
        user_input = input("Enter Target Accuracy (Decimal): ")
        if user_input == "q":
            return "q"
        else:
            try:
                accuracy = float(user_input)
                if 0 <= accuracy <= 1.0:
                    return accuracy
            except ValueError:
                pass
            print("Invalid Input. Please Try Again!")

def get_max_error():
    while 1:
        user_input = input("Enter Max Error (Seconds): ")
        if user_input == "q":
            return "q"
        else:
            try:
                accuracy = float(user_input)
                return accuracy
            except ValueError:
                print("Invalid Input. Please Try Again!")

def get_averaging_window():
    while 1:
        user_input = input("Enter Averaging Window (Odd Number): ")
        if user_input == "q":
            return "q"
        elif user_input.isnumeric() and int(user_input) % 2 != 0:
            return int(user_input)
        else:
            print("Invalid Input. Please Try Again!")

def get_mp3_file():
    user_input = input("Enter file name (Don't forget .mp3): ")
    if user_input == "q":
        return "q"
    return user_input

def get_text():
    user_input = input("Enter text: ")
    if user_input == "q":
        return "q"
    return user_input

