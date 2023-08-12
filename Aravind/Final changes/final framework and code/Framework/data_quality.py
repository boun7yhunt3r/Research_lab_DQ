from functools import wraps
import panel as pn

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

  def calculate_consistency_scores(self, columns_of_interest):
      return calculate_consistency_scores(self.data, columns_of_interest)

  def calculate_relevancy_scores(self, columns_of_interest, outlier_threshold):
      return calculate_relevancy_scores(self.data, columns_of_interest, outlier_threshold)










##For individual columns
  

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
    consistency_scores = []

    for column in columns_of_interest:
        cv = data[column].std() / data[column].mean()
        consistency_score = 1 - cv
        consistency_scores.append({"Column": column, "ConsistencyScore": consistency_score})
    return consistency_scores


# Calculate relevancy scores for selected columns
def calculate_relevancy_scores(data, columns_of_interest, outlier_threshold=3):
    relevancy_scores = []

    for column in columns_of_interest:
        z_scores = (data[column] - data[column].mean()) / data[column].std()
        outliers = data[abs(z_scores) > outlier_threshold][column]
        relevancy_score = len(data[column]) - data[column].isnull().sum() - len(outliers)
        relevancy_scores.append({"Column": column, "RelevancyScore": relevancy_score})

    return relevancy_scores
