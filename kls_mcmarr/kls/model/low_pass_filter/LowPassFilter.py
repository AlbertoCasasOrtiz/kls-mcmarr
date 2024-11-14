
import pandas
from scipy.signal import butter, filtfilt
import numpy as np
import pandas as pd
from kls_mcmarr.kls.capture.global_values import GlobalValues


class LowPassFilter:

    @staticmethod
    def butter_lowpass(cutoff, fs, order=5):
        return butter(order, cutoff, fs=fs, btype='low', analog=False, output='ba')

    @staticmethod
    def butter_lowpass_filter(data, cutoff, fs, order=5):
        coefficient = LowPassFilter.butter_lowpass(cutoff, fs, order=order)
        y = filtfilt(coefficient[0], coefficient[1], data, padlen=0)
        return y

    @staticmethod
    def apply(raw_data):
        # Get column names.
        column_names = list(raw_data.columns.values)

        # Determine the maximum length among all filtered columns.
        max_length = 0

        # Process each column.
        filtered_columns = {}
        for column in column_names:
            column_as_list = raw_data[column].values.tolist()

            # Translate so first value is 0.
            first_value = column_as_list[0]
            column_as_list = [float(x) - float(first_value) for x in column_as_list]

            # Apply low pass filter.
            order = 4
            # Sample rate in Hz.
            fs = GlobalValues.fps
            # Cutoff frequency of the filter in Hz.
            cutoff = 5

            # Filter the data, and plot both the original and filtered signals.
            filtered_column = LowPassFilter.butter_lowpass_filter(column_as_list, cutoff, fs, order)

            # Remove user delay
            first = filtered_column[0]
            index = 0
            for i in range(0, len(filtered_column)):
                if filtered_column[i] > first + first * 0.05 or filtered_column[i] < first - first * 0.05:
                    index = i
                    break
            last = filtered_column[len(filtered_column) - 1]
            for i in reversed(range(0, len(filtered_column))):
                if filtered_column[i] > last + last * 0.05 or filtered_column[i] < last - last * 0.05:
                    index = i
                    break
            filtered_column = filtered_column[:index]

            # Translate filtered column to original position.
            filtered_column = [x + first_value for x in filtered_column]

            # Update max_length if needed
            max_length = max(max_length, len(filtered_column))

            # Store the filtered column in the dictionary
            filtered_columns[column] = filtered_column

        # Fill the filtered columns with NaNs to make them of the same length
        for column in filtered_columns:
            diff = max_length - len(filtered_columns[column])
            if diff > 0:
                filtered_columns[column].extend([np.nan] * diff)

        # Concatenate the filtered columns into a new DataFrame
        filtered_data = pd.DataFrame(filtered_columns)

        return filtered_data
