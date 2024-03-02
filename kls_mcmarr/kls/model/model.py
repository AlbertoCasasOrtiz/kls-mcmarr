import pandas

from kls_mcmarr.mcmarr.model.model import Model as _Model

from kls_mcmarr.kls.model.low_pass_filter.low_pass_filter import LowPassFilter
from kls_mcmarr.kls.capture.mediapipe_wrapper.utils import get_list_landmarks_sorted
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import numpy as np
import os

class Model(_Model):

    def __init__(self, generate_plots=False, output_path="assets/output/capture/"):
        self.generate_plots = generate_plots
        self.output_path = output_path

        if not self.output_path.endswith("/"):
            self.output_path = self.output_path + "/"

        pass

    def model_movement(self, captured_movement, uuid_name=None):
        # Apply low pass filter.
        filtered_movement = LowPassFilter.apply(captured_movement)

        # Remove nans.
        removed_nans = self.remove_nans(filtered_movement)

        if self.generate_plots:
            # TODO: Hardcoded landmark value.
            self.print_scatter_plot("RIGHT_WRIST", removed_nans, (0, len(captured_movement)-1), uuid_name)

        return removed_nans

    def print_scatter_plot(self, landmark_name, dataframe_results, interval, uuid_name):
        if landmark_name + "_x" in dataframe_results and landmark_name + "_y" in dataframe_results:
            # Assuming you have a dataframe named 'df' with columns 'x' and 'y'
            x = dataframe_results[landmark_name + "_x"][interval[0]:interval[1]]
            y = dataframe_results[landmark_name + "_y"][interval[0]:interval[1]]

            # Generate a color array based on a gradient
            colors = np.arange(len(x))

            # Create a scatter plot with color scale
            plt.scatter(x, y, c=colors, cmap='viridis')

            # Create a line plot without markers
            plt.plot(x, y, '-')

            # Set labels for the x and axes
            plt.xlabel('X values')
            plt.ylabel('Y values')

            # Set the title of the plot
            plt.title('Scatter Plot of (x, y) Values with Color Scale')

            # Set the desired range values for the x-axis and y-axis
            x_min = 0.2  # Minimum value for the x-axis
            x_max = 0.65  # Maximum value for the x-axis
            y_min = 0  # Minimum value for the y-axis
            y_max = 1  # Maximum value for the y-axis

            plt.xlim(x_min, x_max)
            plt.ylim(y_min, y_max)

            # Invert the y-axis
            plt.gca().invert_yaxis()

            # Add a color bar to the plot
            plt.colorbar(label='Frame')

            # Save the plot as an image
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
            plt.savefig(self.output_path + uuid_name + ".png", dpi=1200, bbox_inches='tight')

            # Display the plot
            plt.show()
            plt.close()

    def remove_nans(self, df):
        # Remove nans at beginning and end of sequences.
        first_idx = df.first_valid_index()
        last_idx = df.last_valid_index()
        df = df.loc[first_idx:last_idx]

        # Interpolate nans in the middle of sequence.
        df = df.interpolate()

        return df