from functools import wraps
import panel as pn
import pandas as pd
from scipy.stats import skew
from statsmodels.tsa.stattools import adfuller
import numpy as np

class DataQualityChecker:

  def __init__(self, data):
    self.data = data
    self.expectations = []
  
  
  #Kavya changes
  def check_missing_count(self):
        missing_count = self.data.isnull().sum().sum()
        return missing_count

  def calculate_completeness(self):
    total_cells = self.data.size
    missing_cells = self.data.isnull().sum().sum()
    completeness = (total_cells - missing_cells) / total_cells * 100
    return completeness   
  
  def calculate_skewness(self):
        skewness_results = {}

        for column in self.data.columns:
            if pd.api.types.is_numeric_dtype(self.data[column]):
                skewness = self.data[column].skew()
                skewness_results[column] = skewness

        return skewness_results

  def calculate_bias(self):
        # Assuming you have a target column 'TargetColumn' for bias calculation
        target_column = 'TargetColumn'
        bias = self.data[target_column].mean()
        return f"Bias: {bias:.2f}"

  def calculate_stationarity(self):
    stationarity_results = {}

    for column in self.data.columns:
        if pd.api.types.is_numeric_dtype(self.data[column]):
            data = self.data[column].dropna()
            if len(data.unique()) > 1:  # Check if the column has more than one unique value
                result = adfuller(data)
                p_value = result[1]
                is_stationary = p_value < 0.05
                stationarity_results[column] = is_stationary
            else:
                stationarity_results[column] = False  # No variation, consider it non-stationary

    return stationarity_results

  def calculate_time_shifts(self, columns_of_interest):
    time_shift_results = {}

    for column in columns_of_interest:
        target_data = self.data[column].dropna()
        cross_corr = np.correlate(target_data, target_data, mode='full')  # Auto-correlation
        time_shift = cross_corr.argmax() - len(target_data) + 1
        time_shift_results[column] = time_shift

    return time_shift_results
      

   

       
      
        



  def calculate_overall_normalized_consistency(self, columns_of_interest):
        normalized_consistency_scores = self.calculate_normalized_consistency_scores(self.data, columns_of_interest)
        overall_normalized_consistency = sum(score["NormalizedConsistencyScore"] for score in normalized_consistency_scores) / len(columns_of_interest)
        return overall_normalized_consistency

  def calculate_overall_normalized_relevancy(self, columns_of_interest, outlier_threshold=3):
        normalized_relevancy_scores = self.calculate_normalized_relevancy_scores(self.data, columns_of_interest, outlier_threshold)
        overall_normalized_relevancy = sum(score["NormalizedRelevancyScore"] for score in normalized_relevancy_scores) / len(columns_of_interest)
        return overall_normalized_relevancy
  
  
  def calculate_consistency_scores(self, columns_of_interest):
        return calculate_consistency_scores(self.data, columns_of_interest)
  def calculate_relevancy_scores(self, columns_of_interest, outlier_threshold):
        return calculate_relevancy_scores(self.data, columns_of_interest, outlier_threshold)
  
  def calculate_normalized_consistency_scores(self, data, columns_of_interest):

    numeric_columns = [col for col in columns_of_interest if pd.api.types.is_numeric_dtype(data[col])]
    normalized_consistency_scores = []

    for column in numeric_columns:
        cv = data[column].std() / data[column].mean()
        consistency_score = 1 - cv
        normalized_consistency = (consistency_score - 0) / (1 - 0)  # Normalize between 0 and 1
        normalized_consistency_scores.append({"Column": column, "NormalizedConsistencyScore": normalized_consistency})
    print(normalized_consistency_scores)
    return normalized_consistency_scores

  def calculate_normalized_relevancy_scores(self, data, columns_of_interest, outlier_threshold):
    normalized_relevancy_scores = []
    numeric_columns = [col for col in columns_of_interest if pd.api.types.is_numeric_dtype(data[col])]

    for column in numeric_columns:
        z_scores = (data[column] - data[column].mean()) / data[column].std()
        outliers = data[abs(z_scores) > outlier_threshold][column]
        relevancy_score = len(data[column]) - data[column].isnull().sum() - len(outliers)
        normalized_relevancy = (relevancy_score - 0) / (len(data[column]) - 0)  # Normalize between 0 and 1
        normalized_relevancy_scores.append({"Column": column, "NormalizedRelevancyScore": normalized_relevancy})
    print(normalized_relevancy_scores)
    return normalized_relevancy_scores
  

  # def check_completeness(self):

  #     total = self.data.size
  #     missing = self.data.isnull().sum().sum()

  #     completeness = (total - missing) / total * 100

  #     return completeness

  # def check_duplicates(self):

  #   dupes = self.data.duplicated().sum()  

  #   duplicate_pct = dupes / len(self.data) * 100

  #   return duplicate_pct

  # def check_skewness(self):

  #   skew_vals = self.data.skew()
  
  #   return skew_vals
  
  # def check_missing_data(self):

  #   df= self.data

  #   # Set datetime index 
  #   df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H.%M.%S') 
  #   df = df.set_index('Datetime')

  #   # Now resample data to daily frequency  
  #   daily = df.resample('D').mean()
  
  #   # Count number of missing values each day
  #   missing = daily.isna().sum()
  
  #   # Calculate % missing each day
  #   total = len(daily.columns)
  #   missing_pct = missing / total * 100
  
  #   # Identify periods with poor coverage
  #   poor_coverage = missing_pct[missing_pct > 50]
  
  #   # Return summary  
  #   return {
  #     "num_missing": missing,
  #     "pct_missing": missing_pct, 
  #     "poor_coverage": poor_coverage
  #   }



  def expect_column_min_to_be_between(self, column, min_value, max_value):
      between_expectation = _build_min_max_expectation(column, min_value, max_value)
      return between_expectation

  # Other expectation builder helper functions

  def run_checks(self):
    report = []
    for expectation in self.expectations:
      result = expectation(self.data)
      report.append(result)
    return report

# Expectation builder functions



def _build_min_max_expectation(column, min_value, max_value):

  @wraps(column_in_range)
  def func(data):
        violations = column_in_range(data[column], min_value, max_value)
        return violations

  return func

def column_in_range(column, min_value, max_value):
  violations = 0
  for value in column:
      if value < min_value or value > max_value:
          violations += 1
  return violations



def calculate_consistency_scores(data, columns_of_interest):
    numeric_columns = [col for col in columns_of_interest if pd.api.types.is_numeric_dtype(data[col])]
    consistency_scores = []

    for column in numeric_columns:
        cv = data[column].std() / data[column].mean()
        consistency_score = 1 - cv
        consistency_scores.append({"Column": column, "ConsistencyScore": consistency_score})
    print(consistency_scores)
    return consistency_scores




# Calculate relevancy scores for selected columns
def calculate_relevancy_scores(data, columns_of_interest, outlier_threshold=3):
    relevancy_scores = []
     # Filter out non-numeric columns
    numeric_columns = [col for col in columns_of_interest if pd.api.types.is_numeric_dtype(data[col])]

    for column in numeric_columns:
        z_scores = (data[column] - data[column].mean()) / data[column].std()
        outliers = data[abs(z_scores) > outlier_threshold][column]
        relevancy_score = len(data[column]) - data[column].isnull().sum() - len(outliers)
        relevancy_scores.append({"Column": column, "RelevancyScore": relevancy_score})
    print(relevancy_scores)
    return relevancy_scores





