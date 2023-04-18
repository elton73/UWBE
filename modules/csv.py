import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import csv
import datetime
from time import localtime, strftime
from pathlib import Path


def setup_csv():
    # setup csv output
    csv_dir1 = os.path.join(Path(r"C:\Users\ML-2\Documents\GitHub\UWBE"),
                            "csv",
                            f"{datetime.date.today().strftime('%Y-%m-%d')}",
                            "Experiments",
                            "10001009")
    csv_dir2 = os.path.join(Path(r"C:\Users\ML-2\Documents\GitHub\UWBE"),
                            "csv",
                            f"{datetime.date.today().strftime('%Y-%m-%d')}",
                            "Experiments",
                            "10001001")
    if not os.path.exists(csv_dir1):
        os.makedirs(csv_dir1)
    if not os.path.exists(csv_dir2):
        os.makedirs(csv_dir2)

    # Create output csv
    tag1_csv = os.path.join(csv_dir1, f'10001009_T{strftime("%H:%M:%S", localtime()).replace(":", "-")}.csv')
    tag2_csv = os.path.join(csv_dir2, f'10001001_T{strftime("%H:%M:%S", localtime()).replace(":", "-")}.csv')

    tag1_csv_file = open(tag1_csv, 'w', newline='')
    tag1_csv_writer = csv.writer(tag1_csv_file, dialect='excel')
    tag1_csv_writer.writerow(['tag_id', 'x', 'y', 'z', 'zone', 'moving', 'success', 'current_time'])
    tag2_csv_file = open(tag2_csv, 'w', newline='')
    tag2_csv_writer = csv.writer(tag2_csv_file, dialect='excel')
    tag2_csv_writer.writerow(['tag_id', 'x', 'y', 'z', 'zone', 'moving', 'success', 'current_time'])
    return tag1_csv_writer, tag2_csv_writer