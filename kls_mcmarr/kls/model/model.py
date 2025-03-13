import os

import cv2
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np

from kls_mcmarr.kls.model.low_pass_filter.LowPassFilter import LowPassFilter
from kls_mcmarr.mcmarr.model.ModelMcmarr import ModelMcmarr as _Model


class Model(_Model):

    def __init__(self, generate_plots=False, output_path="assets/output/capture/"):
        self.generate_plots = generate_plots
        self.output_path = output_path

        if not self.output_path.endswith("/"):
            self.output_path = self.output_path + "/"

        pass

    def model_movement(self, captured_movement, uuid_name=None):
        # Apply low pass filter.
        # filtered_movement = LowPassFilter.apply(captured_movement)
        filtered_movement = captured_movement

        # Remove nans.
        removed_nans = self.remove_nans(filtered_movement)

        if self.generate_plots:
            self.print_scatter_plot(["RIGHT_WRIST"], removed_nans, (0, len(captured_movement)-1), uuid_name, False)

        return removed_nans

    def print_scatter_plot(self, landmark_names, dataframe_results, interval, uuid_name, show_plot, max_x=1, max_y=1):
        # Check if all specified landmarks exist in the dataframe
        for landmark_name in landmark_names:
            if not (landmark_name + "_x" in dataframe_results and landmark_name + "_y" in dataframe_results):
                print(f"Landmark {landmark_name} is missing in the dataframe.")
                return  # Exit if any landmark is missing

        # Enable/disable interactive plots
        plt.ion() if show_plot else plt.ioff()

        # List of colormaps to assign a unique one for each landmark
        colormaps = ['viridis', 'plasma', 'cividis', 'magma', 'inferno', 'cool', 'spring', 'summer', 'autumn', 'winter']

        # Use a color map for line colors
        line_colors = plt.colormaps['tab10'].resampled(len(landmark_names))

        for i, landmark_name in enumerate(landmark_names):
            # Extract x and y coordinates for the current landmark within the interval
            x = dataframe_results[landmark_name + "_x"][interval[0]:interval[1]]
            y = dataframe_results[landmark_name + "_y"][interval[0]:interval[1]]

            # Generate a color array for the current landmark based on a gradient
            color_array = np.arange(len(x))

            # Select the colormap for this landmark (loop back if more landmarks than colormaps)
            cmap = colormaps[i % len(colormaps)]

            # Plot scatter and line for each landmark with a unique colormap
            plt.scatter(x, y, c=color_array, cmap=cmap, label=landmark_name, alpha=0.6)
            plt.plot(x, y, '-', color=line_colors(i), alpha=0.8)

        # Set labels for the x and y axes
        plt.xlabel('Image Width Ratio')
        plt.ylabel('Image Height Ratio')

        # Set the title of the plot
        plt.title('Landmark Positions Over Time')

        # Set the desired range values for the x-axis and y-axis
        plt.xlim(0, max_x)
        plt.ylim(0, max_y)

        # Invert the y-axis
        plt.gca().invert_yaxis()

        # Add a color bar and legend
        plt.colorbar(label='Frame Number')
        plt.legend()

        # Save the plot as an image
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        plt.savefig(self.output_path + uuid_name + ".png", dpi=1200, bbox_inches='tight')

        # Display the plot
        if show_plot:
            plt.show()

        # Close the plot
        plt.close()

    def overlay_scatter_on_video(self, video_path, landmark_names, dataframe_results, interval, output_video_path,
                                 max_x=1, max_y=1, draw_function=None):
        # Check if all specified landmarks exist in the dataframe
        for landmark_name in landmark_names:
            if not (landmark_name + "_x" in dataframe_results and landmark_name + "_y" in dataframe_results):
                print(f"Landmark {landmark_name} is missing in the dataframe.")
                return  # Exit if any landmark is missing

        # Initialize video capture and get properties
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

        # List of colormaps to assign a unique one for each landmark
        colormaps = ['viridis', 'plasma', 'cividis', 'magma', 'inferno', 'cool', 'spring', 'summer', 'autumn', 'winter']
        line_colors = plt.colormaps['tab10'].resampled(len(landmark_names))

        # Go to start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, interval[0])

        # Loop through the specified frame interval
        for frame_num in range(interval[0], interval[1]):
            ret, frame = cap.read()
            if not ret:
                break  # End of video

            # Start a new figure for each frame with dimensions matching the video frame
            fig, ax = plt.subplots(figsize=(frame_width / 100, frame_height / 100), dpi=100)

            # Set transparent background for both figure and axis
            fig.patch.set_alpha(0)  # Make figure background transparent
            ax.patch.set_alpha(0)  # Make axis background transparent

            for i, landmark_name in enumerate(landmark_names):
                # Extract x and y coordinates for the current landmark up to the current frame
                x = dataframe_results[landmark_name + "_x"][:frame_num]
                y = dataframe_results[landmark_name + "_y"][:frame_num]

                # Generate a color array for the current landmark based on a gradient
                color_array = np.arange(len(x))

                # Select the colormap for this landmark
                cmap = colormaps[i % len(colormaps)]

                # Plot scatter and line for each landmark
                ax.scatter(x, y, c=color_array, cmap=cmap, alpha=0.6)
                ax.plot(x, y, '-', color=line_colors(i), alpha=0.8)

            # Set plot limits to ensure the plot area exactly matches the video frame dimensions
            ax.set_xlim(0, max_x)
            ax.set_ylim(0, max_y)
            ax.invert_yaxis()

            # Remove all elements except the plot area
            ax.axis('off')
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

            # Call the draw_function if provided
            if draw_function:
                draw_function(ax)  # Pass ax and frame_num to draw_function

            # Render the plot to an image array
            fig.canvas.draw()
            plot_img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            plot_img = plot_img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            plot_img = cv2.resize(plot_img, (frame_width, frame_height))

            # Overlay the plot image onto the video frame
            combined_frame = cv2.addWeighted(frame, 0.6, plot_img, 0.4, 0)

            # Write the combined frame to the output video
            out.write(combined_frame)

            # Clear the plot for the next frame
            plt.close(fig)

        # Release resources
        cap.release()
        out.release()
        print(f"Overlay video saved to {output_video_path}")

    def side_by_side_scatter_on_video(self, video_path, landmark_names, dataframe_results, interval, output_video_path,
                                      max_x=1, max_y=1):
        # Check if all specified landmarks exist in the dataframe
        for landmark_name in landmark_names:
            if not (landmark_name + "_x" in dataframe_results and landmark_name + "_y" in dataframe_results):
                print(f"Landmark {landmark_name} is missing in the dataframe.")
                return  # Exit if any landmark is missing

        # Initialize video capture and get properties
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # New output frame width to accommodate side-by-side layout
        output_width = frame_width * 2
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (output_width, frame_height))

        # List of colormaps to assign a unique one for each landmark
        colormaps = ['viridis', 'plasma', 'cividis', 'magma', 'inferno', 'cool', 'spring', 'summer', 'autumn', 'winter']
        line_colors = plt.colormaps['tab10'].resampled(len(landmark_names))

        # Loop through the specified frame interval
        for frame_num in range(interval[0], interval[1]):
            ret, frame = cap.read()
            if not ret:
                break  # End of video

            # Start a new figure for each frame
            plt.figure(figsize=(8, 6))

            for i, landmark_name in enumerate(landmark_names):
                # Extract x and y coordinates for the current landmark up to the current frame
                x = dataframe_results[landmark_name + "_x"][:frame_num]
                y = dataframe_results[landmark_name + "_y"][:frame_num]

                # Generate a color array for the current landmark based on a gradient
                color_array = np.arange(len(x))

                # Select the colormap for this landmark
                cmap = colormaps[i % len(colormaps)]

                # Plot scatter and line for each landmark
                plt.scatter(x, y, c=color_array, cmap=cmap, label=landmark_name, alpha=0.6)
                plt.plot(x, y, '-', color=line_colors(i), alpha=0.8)

            # Configure plot aesthetics
            plt.xlabel('Image Width Ratio')
            plt.ylabel('Image Height Ratio')
            plt.title('Landmark Positions Over Time')
            plt.xlim(0, max_x)
            plt.ylim(0, max_y)
            plt.gca().invert_yaxis()
            plt.colorbar(label='Frame Number')
            plt.legend()

            # Render the plot to an image array
            plt.draw()
            plot_img = np.frombuffer(plt.gcf().canvas.tostring_rgb(), dtype=np.uint8)
            plot_img = plot_img.reshape(plt.gcf().canvas.get_width_height()[::-1] + (3,))
            plot_img = cv2.resize(plot_img, (frame_width, frame_height))

            # Combine frame and plot image side by side
            combined_frame = np.hstack((frame, plot_img))

            # Write the combined frame to the output video
            out.write(combined_frame)

            # Clear the plot for the next frame
            plt.clf()

        # Release resources
        cap.release()
        out.release()
        plt.close()
        print(f"Side-by-side video saved to {output_video_path}")

    def remove_nans(self, df):
        # Remove nans at beginning and end of sequences.
        first_idx = df.first_valid_index()
        last_idx = df.last_valid_index()
        df = df.loc[first_idx:last_idx]

        # Interpolate nans in the middle of sequence.
        df = df.interpolate()

        return df
