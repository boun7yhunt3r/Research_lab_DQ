from functools import wraps
import panel as pn
import pandas as pd
from scipy.stats import skew
from statsmodels.tsa.stattools import adfuller
from scipy.signal import correlate


class Improve_DQ:

    def __init__(self, data):
        self.data = data
        self.expectations = []

    def improve_stationarity(self, column_name):
        data = self.data[column_name].dropna()

        # Check if data contains any non-numeric values
        if not data.apply(lambda x: isinstance(x, (int, float))).all():
            print(f"Column {column_name} contains non-numeric values. Skipping differencing.")
            return None

        # Apply differencing to remove non-stationary drifts
        diff_data = data.diff().dropna()

        # Create a copy of the original data and update it with the differenced values
        improved_data = self.data.copy()
        improved_data.loc[diff_data.index, column_name] = diff_data

        return improved_data
    
    def improve_time_shifts(self, target_column):
        target_data = self.data[target_column].dropna()

        # Calculate auto-correlation
        cross_corr = correlate(target_data, target_data, mode='full')
        time_shift = cross_corr.argmax() - len(target_data) + 1

        # Apply time shift correction using interpolation
        shifted_data = target_data.shift(time_shift)
        improved_data = shifted_data.interpolate()

        # Update the original DataFrame with the improved data
        self.data[target_column] = improved_data

        return self.data