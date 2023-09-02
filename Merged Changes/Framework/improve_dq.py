from functools import wraps
import pandas as pd
from scipy.stats import skew
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy.signal import correlate

class Improve_DQ:

    def __init__(self, data):
        self.data = data
        self.expectations = []

#Deepthy
    def count_missing_values(self):
        return self.data.isnull().sum()

    def impute_missing_values(self, method, column_name=None, seasonal_period=None, window_size=None):
        if method == 'forward_back_fill':
            imputed_data = self.impute_forward_back_fill(column_name)
        elif method == 'linear_interpolation':
            imputed_data = self.impute_linear_interpolation(column_name)
        elif method == 'seasonal_decomposition':
            imputed_data = self.impute_seasonal_decomposition(column_name, period= 24)
        
        else:
            raise ValueError("Invalid imputation method")
        
        return imputed_data

    def impute_forward_back_fill(self, column_name):
        data = self.data[column_name].copy()
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)
        return data

    def impute_linear_interpolation(self, column_name):
        data = self.data[column_name].copy()
        data.interpolate(method='linear', inplace=True)
        #self.imputed_columns.append(column_name)
        return data


    def impute_seasonal_decomposition(self, column_name, period):
        data = self.data.copy()

    # Convert 'Date' and 'Time' strings to datetime objects with the correct format
        data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y', dayfirst=True)
        data['Time'] = pd.to_timedelta(data['Time'].str.replace('.', ':'))

    # Combine 'Date' and 'Time' into a single 'Datetime' column
        data['Datetime'] = data['Date'] + data['Time']

    # Drop 'Date' and 'Time' columns if not needed
        data = data.drop(['Date', 'Time'], axis=1)

    # Handle missing values by forward filling
        data.fillna(method='ffill', inplace=True)

    # Set 'Datetime' as the index of the DataFrame
        data.set_index('Datetime', inplace=True)

    # Perform seasonal decomposition on the specified column
        column_series = data[column_name]
        decomposition = seasonal_decompose(column_series, model='additive', period=period)

    # Extract the seasonal component
        seasonal_component = decomposition.seasonal

    # Impute missing values using the seasonal component
        imputed_series = column_series.fillna(seasonal_component)

        return imputed_series


    # In the Improve_DQ class, modify the plot_air_quality_data method as follows:

    def plot_air_quality_data(self, timestamp_col, column_name, imputed_data=None, resampled_data=None):
        data = self.data.copy()

        # Convert 'Date' strings to datetime objects with the correct format
        data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y', dayfirst=True)
    
        # Parse 'Time' strings to create a timedelta column
        data['Time'] = data['Time'].str.replace('.', ':')  # Replace dot with colon
        data['Time'] = data['Time'].str.extract('(\d+:\d+:\d+)')[0]  # Extract HH:MM:SS format
        data['Time'] = pd.to_timedelta(data['Time'])
    
        # Combine 'Date' and 'Time' into 'Datetime' column
        data['timestamp'] = data['Date'] + data['Time']
        data.sort_values(by=timestamp_col, inplace=True)

        # Set the timestamp column as the index for the original data
        data.set_index(timestamp_col, inplace=True)

        plt.figure(figsize=(10, 6))
        #plt.plot(data.index, data[column_name], marker='o', linestyle='-', color='b', label='Original Data')
        plt.xlabel('Timestamp')

        plt.ylabel(f'{column_name} Concentration')
        plt.title('Air Quality Data')

        if imputed_data is not None:
            plt.plot(data.index, imputed_data, marker='s', linestyle='-', color='g', label='Imputed Data')

        if resampled_data is not None:
            plt.plot(resampled_data.index, resampled_data, marker='x', linestyle='--', color='r', label='Resampled Data')

        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def align_frequencies(self, timestamp_col, value_col, target_frequency):
        data = self.data.copy()
        # Convert 'Date' strings to datetime objects with the correct format
        data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y', dayfirst=True)
        # Replace dots with colons to create a time format pandas can understand
        data['Time'] = data['Time'].str.replace('.', ':')
        # Convert 'Time' strings to timedelta objects (assuming the 'Time' column contains hour values)
        data['Time'] = pd.to_timedelta(data['Time'])

        # Combine 'Date' and 'Time' into 'Datetime' column
        data['timestamp'] = data['Date'] + data['Time']

        # Set the 'timestamp_col' column as the index
        data.set_index(timestamp_col, inplace=True)

        # Resample time series to the desired frequency and aggregate data
        resampled_data = data[value_col].resample(target_frequency).median()

        return resampled_data
#Aravind 
    def handle_duplicates(self):
        # Remove duplicates and keep the first occurrence
        print("initial rows")
        initial_rows = len(self.data)
        print(initial_rows)
        original_data = self.data.copy()  # Make a copy of the original data
        self.data = self.data.drop_duplicates(keep='first')
        
        removed_rows = original_data[original_data.duplicated(keep='first')]
        print("Rows removed:")
        print(removed_rows)
        
        final_rows = len(self.data)
        duplicates_dropped = initial_rows - final_rows
        return duplicates_dropped
    
    def smooth_outliers(self, columns_of_interest=None, window_size=3, threshold=2):
        if columns_of_interest is None:
            columns_of_interest = self.data.select_dtypes(include=['number']).columns
        
        # Create a new DataFrame for smoothed data
        smoothed_data = self.data.copy()

        # Create the 'is_outlier' column with default values (False) for all columns
        smoothed_data['is_outlier'] = False

        # Create the 'smoothened_rows' column to store smoothened column names for each row
        smoothed_data['smoothened_rows'] = ''

        # Loop through columns of interest
        for column in columns_of_interest:
            if column not in smoothed_data.select_dtypes(include=['number']).columns:
                print(f"Ignoring column '{column}' because it's not numeric.")
                continue

            # Apply a moving average to smooth the time series
            smoothed_data[f'{column}_smoothed'] = smoothed_data[column].rolling(window=window_size).mean()

            # Calculate the z-score for each data point
            z_scores = (smoothed_data[column] - smoothed_data[f'{column}_smoothed']) / smoothed_data[column].std()

            # Identify and mark outliers based on the z-score threshold
            smoothed_data[f'{column}_is_outlier'] = z_scores.abs() > threshold

            # Update 'is_outlier' column
            smoothed_data['is_outlier'] = smoothed_data['is_outlier'] | smoothed_data[f'{column}_is_outlier']

            # Update 'smoothened_rows' column
            smoothed_data.loc[smoothed_data[f'{column}_is_outlier'], 'smoothened_rows'] += f'{column}, '

        # Remove trailing comma from 'smoothened_rows'
        smoothed_data['smoothened_rows'] = smoothed_data['smoothened_rows'].str.rstrip(', ')

        return smoothed_data

#Kavya
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