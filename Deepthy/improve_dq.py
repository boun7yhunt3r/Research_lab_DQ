from functools import wraps
import panel as pn
import pandas as pd
from scipy.stats import skew
from statsmodels.tsa.stattools import adfuller

class Improve_DQ:

    def __init__(self, data):
        self.data = data
        self.expectations = []

    def identify_missing_values(self):
        missing_values = self.data.isnull().sum()
        print("missing values")
        print(missing_values)
        return missing_values
        

    def impute_missing_values(self, method='mean'):
        if method == 'mean':
            imputed_data = self.data.fillna(self.data.mean())
        elif method == 'median':
            imputed_data = self.data.fillna(self.data.median())
        else:
            imputed_data = self.data.fillna(method)
        print("imputed data")
        print(imputed_data)
        return imputed_data
        missing_values = self.identify_missing_values(self.data)
        print("\nMissing Values:")
        print(missing_values)

        imputed_data_mean = self.impute_missing_values(self.data, method='mean')
        print("\nImputed Data (Mean):")
        print(imputed_data_mean)

        imputed_data_median = self.impute_missing_values(self.data, method='median')
        print("\nImputed Data (Median):")
        print(imputed_data_median)

# Example usage

        #print("Original Data:")
        #print(self.data)


    def interpolate_time_series(self, method='linear'):
        interpolated_data = self.data.interpolate(method=method)
        
        print("\nInterpolated Data:")
        print(interpolated_data)
        return interpolated_data

    def impute_time_series(self, window_size=3):
        imputed_data = self.data.fillna(self.data.rolling(window=window_size, min_periods=1).mean())
        print("\nImputed Data:")
        print(imputed_data)
        return imputed_data

    