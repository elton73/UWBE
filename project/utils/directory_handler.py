import tkinter as tk
from tkinter import filedialog
import csv
import os

class DirectoryHandler:
    def __init__(self):
        self.file_paths = []
        self.output_directory = None

        self.csv_file = None
        self.csv_writer = None

    def setup_csv(self, name):
        #create output directory if not exists
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        count = 1
        output_csv = os.path.join(self.output_directory, f"{name}_{count}.csv")
        while os.path.exists(output_csv):
            count += 1
            output_csv = os.path.join(self.output_directory, f"{name}_{count}.csv")
        self.csv_file = open(output_csv, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)

    def write_csv(self, data):
        self.csv_writer.writerow(data)

    def read_csvs(self):
        if self.file_paths == "q":
            return "q"
        elif not self.file_paths:
            print("No Files")
            return "q"
        datasets = []
        for file_path in self.file_paths:
            file = open(file_path, "r")
            dataset = list(csv.reader(file, delimiter=","))
            file.close()
            datasets.append(dataset)
        return datasets

    def close_csvs(self):
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None

    def choose_csvs(self):
        root = tk.Tk()
        root.withdraw()
        # Open the file dialog for multiple CSV file selection
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if file_paths:
            self.file_paths = file_paths
        else:
            print("No CSV files selected.")
            return "q"

    def choose_single_csv(self):
        root = tk.Tk()
        root.withdraw()
        # Open the file dialog for a single CSV file selection
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_paths = [file_path]
        else:
            print("No CSV file selected.")
            return "q"

    def choose_output_directory(self):
        root = tk.Tk()
        root.withdraw()
        # Open the file dialog for directory selection
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.output_directory = directory_path
        else:
            print("No directory selected.")
            return "q"



