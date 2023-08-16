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
