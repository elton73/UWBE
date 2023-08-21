"""
Find standard deviation and mean of uwb noise experiment data.
"""

from project.utils.directory_handler import DirectoryHandler
import ast
import statistics

dir_handler = DirectoryHandler()

GOLD_STANDARD_COORDINATES = [2961, 9453]

def main():
    print("Choose UWB Noise CSVs")
    out = dir_handler.choose_csvs()
    if out == "q":
        return
    datasets = dir_handler.read_csvs()
    for dataset in datasets:
        title = dataset.pop(0)
        x = []
        y = []
        for data in dataset:
            x.append(ast.literal_eval(data[0])[0])
            y.append(ast.literal_eval(data[0])[1])

        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        std_x = statistics.stdev(x)
        std_y = statistics.stdev(y)

        print("\n")
        print(title)
        print(f"mean_x: {int(round(mean_x, 0))}")
        print(f"mean_y: {int(round(mean_y, 0))}")
        print(f"std_x: {int(round(std_x, 0))}")
        print(f"std_y: {int(round(std_y, 0))}")
        print(f"mean_error_x: {int(round(mean_x - GOLD_STANDARD_COORDINATES[0], 0))}")
        print(f"mean_error_y: {int(round(mean_y - GOLD_STANDARD_COORDINATES[1], 0))}")

if __name__ == '__main__':
    main()

