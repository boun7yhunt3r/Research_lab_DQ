from functools import wraps
import panel as pn
import pandas as pd
from scipy.stats import skew
from statsmodels.tsa.stattools import adfuller

class DataQualityChecker:

  def __init__(self, data):
    self.data = data
    self.expectations = []

## For entire data set
  def display_first_few_rows(self):
      return pn.pane.Str("Display the first few rows of the dataset\n" + str(self.data.head()))

  def display_summary_stats(self):
      return pn.pane.Str("\nSummary statistics of the dataset\n" + str(self.data.describe()))

  def display_missing_values(self):
      return pn.pane.Str("\nCheck for missing values\n" + str(self.data.isnull().sum()))

  def display_skewness(self):
      skewness = self.data.skew()
      return pn.pane.Str("\nAssess skewness of the data\n" + str(skewness))

  #def calculate_consistency_scores(self, columns_of_interest):
      #return calculate_consistency_scores(self.data, columns_of_interest)
  
  
  def calculate_consistency_scores(self, columns_of_interest):
        return calculate_consistency_scores(self.data, columns_of_interest)
  def calculate_relevancy_scores(self, columns_of_interest, outlier_threshold):
      return calculate_relevancy_scores(self.data, columns_of_interest, outlier_threshold)

  def check_completeness(self):

      total = self.data.size
      missing = self.data.isnull().sum().sum()

      completeness = (total - missing) / total * 100

      return completeness

  def check_duplicates(self):

    dupes = self.data.duplicated().sum()  

    duplicate_pct = dupes / len(self.data) * 100

    return duplicate_pct

  def check_skewness(self):

    skew_vals = self.data.skew()
  
    return skew_vals
  
  def check_missing_data(self):

    df= self.data

    # Set datetime index 
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H.%M.%S') 
    df = df.set_index('Datetime')

    # Now resample data to daily frequency  
    daily = df.resample('D').mean()
  
    # Count number of missing values each day
    missing = daily.isna().sum()
  
    # Calculate % missing each day
    total = len(daily.columns)
    missing_pct = missing / total * 100
  
    # Identify periods with poor coverage
    poor_coverage = missing_pct[missing_pct > 50]
  
    # Return summary  
    return {
      "num_missing": missing,
      "pct_missing": missing_pct, 
      "poor_coverage": poor_coverage
    }


##For individual columns

  def check_stationarity(self):

    data = self.data['CO(GT)'].dropna()

    # Run Dickey-Fuller test
    result = adfuller(data)

    stat = result[0]
    p_value = result[1]

    is_stationary = p_value < 0.05
    print(is_stationary)
    # Return Series with stationarity result
    stationary = pd.Series([is_stationary], index=['Stationary'])

    return stationary  

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
