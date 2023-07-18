import os
import csv
from config import TAG_ID

def get_tag_id():
    user_input = input("Enter tag id: ")
    if user_input == "q":
        return "q"
    return user_input

def get_patient_id():
    user_input = input("Enter patient id: ")
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

def choose_setup_number():
    while 1:
        user_input = input("Enter Setup Number: ")
        if user_input.isnumeric() or user_input == "q":
            return user_input
        else:
            print("Invalid Input. Please Try Again!")

def choose_csvs():
    datasets = []
    indexes = []
    while 1:
        setup_type = str(input("Enter setup type number: "))
        if "q" in setup_type:  # quit calibration
            return "q"
        path = os.path.join(os.getcwd(),
                            "../../",
                            "csv",
                            TAG_ID,
                            "experiments",
                            "moving_experiment",
                            "ILS",
                            f"setup_{setup_type}",
                            "raw_data")
        if not os.path.exists(path):
            print(path)
            print("No such path! Please Try Again")
        else:
            break
    print("Enter s to begin or q to quit")
    while 1:
        counter = str(input("Enter an experiment number: "))
        if "q" in counter:  # quit calibration
            return "q"
        elif "s" in counter:  # begin calibration
            if len(datasets) > 0:
                return setup_type, datasets, indexes
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
                                f"setup_{setup_type}",
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

def get_plot_type():
    print("Enter Plot Type Here! 1. Plot raw coordinates; 2. Plot averaged coordinates; 3. Plot both")
    while 1:
        user_input = input("Enter Plot Type: ")
        if user_input == '1' or user_input == '2' or user_input == '3' or user_input == "q":
            return user_input
        else:
            print("Invalid Input. Please Try Again!")

def get_calibration_plot_type():
    print("1. Plot Count; 2. Plot Speed Threshold; 3. Plot Averaging Window; 4. Plot All")
    while 1:
        user_input = input("Enter Plot Type: ")
        if user_input == '1' or user_input == '2' or user_input == '3' or user_input == '4' or user_input == "q":
            return user_input
        else:
            print("Invalid Input. Please Try Again!")

def get_target_accuracy():
    while 1:
        user_input = input("Enter target accuracy (Example 0.9): ")
        if user_input == "q":
            return "q"
        else:
            try:
                if 0 <= user_input <= 1:
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

def get_zed_csv():
    datasets = []
    while 1:
        path = str(input("Enter csv path: "))
        if "q" in path:  # quit calibration
            return "q"
        else:
            if not os.path.exists(path):
                print(path)
                print("No such file! Please Try Again")
            else:
                try:
                    file = open(path, "r")
                    data = list(csv.reader(file, delimiter=","))
                    file.close()
                    datasets.append(data)
                    return datasets
                except:
                    print("Error opening file! Please Try Again")

def get_object_id():
    user_input = input("Enter object id: ")
    if user_input == "q":
        return "q"
    return user_input
