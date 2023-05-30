
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
    user_input = input("Enter Moving Time: ")
    if user_input == "q":
        if tag:
            tag.close_csv()
        raise SystemExit
    return user_input

def get_transition_count(tag=None):
    user_input = input("Enter Number Of Transitions: ")
    if user_input == "q":
        if tag:
            tag.close_csv()
        raise SystemExit
    return user_input
