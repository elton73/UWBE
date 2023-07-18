"""
Plot coordinates
"""
import matplotlib
import ast
from matplotlib import pyplot as plt
from project.utils.directory_handler import DirectoryHandler
from project.experiment_tools.tag_analyze import TagAnalyzer
from project.utils.data import RawData
from config import TAG_ID
import os
import project.utils.inputs as inputs

tag = TagAnalyzer(TAG_ID, data_processor="1")
matplotlib.rcParams['interactive'] = True
dir_handler = DirectoryHandler()
img = plt.imread("setups/ils.png")

save = False

# averaging windows to test
averaging_window_threshold_min = 3
averaging_window_threshold_max = 71
averaging_window_threshold_increment = 2

def main():
    # choose output type
    user_input = inputs.get_plot_type()
    if user_input == "q":
        return
    plot_type = user_input

    # get single csv
    print("Choose a UWB CSV")
    user_input = dir_handler.choose_single_csv()
    if user_input == "q":
        return

    datasets = dir_handler.read_csvs()

    # get output directory to save plot
    if save:
        print("Choose where files should be saved")
        dir_handler.choose_output_directory()
        user_input = dir_handler.choose_output_directory()
        if user_input == "q":
            return

    if plot_type == "1":
        plot_raw_coordinates(datasets)
    elif plot_type == "2":
        plot_averaged_coordinates(datasets, plot_both=False)
    elif plot_type == "3":
        plot_averaged_coordinates(datasets, plot_both=True)
def plot_raw_coordinates(datasets):
    for dataset in datasets:
        dataset.pop(0)
        x = []
        y = []
        for data in dataset:
            x.append(ast.literal_eval(data[0])[0])
            y.append(ast.literal_eval(data[0])[1])
        plt.imshow(img, extent=[0, 11400, 0, 10600]) # change the size of the image to match real-life size
        plt.scatter(x, y, s=20)

        if save:
            # creating output file name for image
            count = 1
            output = os.path.join(dir_handler.output_directory, f"img_{count}.png")
            while os.path.exists(output):
                count += 1
                output = os.path.join(dir_handler.output_directory, f"img_{count}.png")
            plt.savefig(output)
        plt.show()

def plot_averaged_coordinates(datasets, plot_both):
    dataset = datasets[0]
    dataset.pop(0)
    # Set window sizes to plot
    averaging_windows = []
    averaging_window_threshold = averaging_window_threshold_min
    while averaging_window_threshold <= averaging_window_threshold_max:
        averaging_windows.append(averaging_window_threshold)
        averaging_window_threshold += averaging_window_threshold_increment

    for averaging_window in averaging_windows:
        tag.data_processor.reset()
        tag.data_processor.averaging_window_threshold = averaging_window
        tag.data_processor.index = averaging_window // 2
        x_aver = []
        y_aver = []
        if plot_both:
            x_raw = []
            y_raw = []
        for d in dataset:
            # try:
            tag.add_data(RawData(ast.literal_eval(d[0]), d[1], float(d[2]), d[3]))
            if tag.data_processor.dataset:
                x_aver.append(tag.data_processor.dataset[-1].coordinates[0])
                y_aver.append(tag.data_processor.dataset[-1].coordinates[1])
            if plot_both:
                x_raw.append(ast.literal_eval(d[0])[0])
                y_raw.append(ast.literal_eval(d[0])[1])

            # except Exception as e:
            #     print(e)
            #     print("Process Failed. Please check that CSV files were correct.")
            #     return
        plt.imshow(img, extent=[0, 11400, 0, 10600])  # change the size of the image to match real-life size
        plt.scatter(x_aver, y_aver, s=5, c='b', label='averaged_coordinates')
        plt.title(f"Averaging Window: {averaging_window}")
        if plot_both:
            plt.scatter(x_raw, y_raw, s=5, c='g', label='raw_coordinates')
            plt.legend(loc='upper left')
        plt.show()

if __name__ == '__main__':
    main()
