class ProgressBar:
    def __init__(self):
        self.progress = 0.0
        self.max = 100.0

    def set_max(self, max_value):
        self.max = max_value

    def update_bar(self, increment=1):
        self.progress += increment

    def reset(self):
        self.progress = 0.0

    def print_output(self):
        print(f"\r{self.progress}/{self.max}", end="")

def find_common_settings(settings_list):
    if len(settings_list) < 2:
        return settings_list[0]
    common_settings = settings_list.pop(0)
    for setting in settings_list:
        common_settings = set(common_settings).intersection(setting)
    return common_settings

