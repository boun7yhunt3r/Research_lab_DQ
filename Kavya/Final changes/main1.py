##import data_quality as dq
import panel as pn
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.request
from zipfile import ZipFile
from importlib import reload

from Framework.data_quality import DataQualityChecker
from Visualization.dashboard import Dashboard

filename = "AirQualityUCI.zip"

# Extract the CSV file from the ZIP file
with ZipFile(filename, "r") as zip_file:
    csv_file = zip_file.open("AirQualityUCI.csv")

    # Read the CSV file into a DataFrame
    data = pd.read_csv(csv_file, sep=";", decimal=",")


# Create an instance of DataQualityChecker
checker = DataQualityChecker(data)
columns_of_interest = ["CO(GT)", "PT08.S1(CO)", "NMHC(GT)", "C6H6(GT)", "PT08.S2(NMHC)", "NOx(GT)",
                       "PT08.S3(NOx)", "NO2(GT)", "PT08.S4(NO2)", "PT08.S5(O3)", "T", "RH", "AH"]


# Add expectations and calculate scores
Consistency_scores = checker.calculate_consistency_scores(columns_of_interest)
Relevancy_scores = checker.calculate_relevancy_scores(columns_of_interest, 3)

""" print("Check completeness")
print(checker.check_completeness())

print("Check duplicates")
print(checker.check_duplicates())

print("Check skewtness")
print(checker.check_skewness())

print("Check missing data")
print(checker.check_missing_data())


print("Check check_stationarity column")
print(checker.check_stationarity()) """

# Define columns of interest
all_columns = data.columns.tolist()

# Create interactive dropdown for selecting columns
column_dropdown = pn.widgets.MultiChoice(
    name="Select Columns of Interest",
    options=all_columns
)

# Create placeholders for the plots and indicators
fig_consistency = pn.pane.Plotly()
fig_relevancy = pn.pane.Plotly()
circle_overall_consistency = pn.pane.Plotly()
circle_overall_relevancy = pn.pane.Plotly()

# Create a function to update plots and scores
def update_plots(event):
    selected_columns = column_dropdown.value
    selected_columns = [col for col in selected_columns if pd.api.types.is_numeric_dtype(data[col])]
    consistency_scores = checker.calculate_consistency_scores(selected_columns)
    print(type(consistency_scores))
    relevancy_scores = checker.calculate_relevancy_scores(selected_columns, 3)
    print(type(relevancy_scores))

    consistency_df = pd.DataFrame(consistency_scores, columns=["Column", "ConsistencyScore"])
    relevancy_df = pd.DataFrame(relevancy_scores, columns=["Column", "RelevancyScore"])

    consistency_df["ConsistencyPercentage"] = ((consistency_df["ConsistencyScore"]/ len(selected_columns)) * 100).round(2)
    relevancy_df["RelevancyPercentage"] = ((relevancy_df["RelevancyScore"] / len(selected_columns)) * 100).round(2)

    fig_consistency.object = px.bar(consistency_df, x="Column", y="ConsistencyScore", title="Consistency Scores")
    fig_relevancy.object = px.bar(relevancy_df, x="Column", y="RelevancyScore", title="Relevancy Scores")
    
    overall_consistency = consistency_df["ConsistencyScore"].sum() / (len(selected_columns) * len(data))
    overall_relevancy = relevancy_df["RelevancyScore"].sum() / (len(selected_columns) * len(data))
    
    circle_overall_consistency.object = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_consistency * 100,
        title="Overall Consistency",
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [None, 100]}}
    ))
    
    circle_overall_relevancy.object = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_relevancy * 100,
        title="Overall Relevancy",
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [None, 100]}}
    ))

# Link the dropdown widget to the update function
column_dropdown.param.watch(update_plots, "value")

# Create the layout
layout = pn.Column(
    "# Air Quality Data Quality Dashboard",
    column_dropdown,
    "## Overall Scores",
    pn.Row(
        circle_overall_consistency,
        circle_overall_relevancy
    ),
    "## Consistency Scores",
    fig_consistency,
    "## Relevancy Scores",
    fig_relevancy
)
# Display the layout
layout.servable()

#report = checker.run_checks()
#print(report)

