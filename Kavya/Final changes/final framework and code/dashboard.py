import panel as pn
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from zipfile import ZipFile
import urllib.request
from Framework.data_quality import DataQualityChecker

# Download the ZIP file
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00360/AirQualityUCI.zip"
filename = "AirQualityUCI.zip"
urllib.request.urlretrieve(url, filename)

# Extract the CSV file from the ZIP file
with ZipFile(filename, "r") as zip_file:
    csv_file = zip_file.open("AirQualityUCI.csv")

    # Read the CSV file into a DataFrame
    data = pd.read_csv(csv_file, sep=";", decimal=",")

# Create DataQualityChecker instance
checker = DataQualityChecker(data)

# Define columns of interest
all_columns = data.columns.tolist()
columns_of_interest = ["CO(GT)", "PT08.S1(CO)", "NMHC(GT)", "C6H6(GT)", "PT08.S2(NMHC)", "NOx(GT)",
                       "PT08.S3(NOx)", "NO2(GT)", "PT08.S4(NO2)", "PT08.S5(O3)", "T", "RH", "AH"]

# Create interactive dropdown for selecting columns
column_dropdown = pn.widgets.MultiChoice(
    name="Select Columns of Interest",
    options=all_columns,
    value=columns_of_interest
)

# Calculate consistency and relevancy scores
consistency_scores = checker.calculate_consistency_scores(columns_of_interest)
relevancy_scores = checker.calculate_relevancy_scores(columns_of_interest, 3)

# Convert scores to DataFrame for calculations
consistency_df = pd.DataFrame(consistency_scores)
relevancy_df = pd.DataFrame(relevancy_scores)

# Calculate percentage scores
total_columns = len(columns_of_interest)
consistency_df["ConsistencyPercentage"] = (consistency_df["ConsistencyScore"] * 100).round(2)
relevancy_df["RelevancyPercentage"] = ((relevancy_df["RelevancyScore"] / total_columns) * 100).round(2)

# Calculate overall scores
overall_consistency = consistency_df["ConsistencyScore"].mean()
overall_relevancy = relevancy_df["RelevancyScore"].sum() / (total_columns * len(data))

# Create interactive plots using Plotly Express
fig_consistency = px.bar(consistency_df, x="Column", y="ConsistencyScore", title="Consistency Scores")
fig_relevancy = px.bar(relevancy_df, x="Column", y="RelevancyScore", title="Relevancy Scores")

# Create circular indicators for percentages using Plotly RadialGauge
circle_overall_consistency = go.Figure(go.Indicator(
    mode="gauge+number",
    value=overall_consistency * 100,
    title="Overall Consistency",
    domain={'x': [0, 1], 'y': [0, 1]},
    gauge={'axis': {'range': [None, 100]}}
))

circle_overall_relevancy = go.Figure(go.Indicator(
    mode="gauge+number",
    value=overall_relevancy * 100,
    title="Overall Relevancy",
    domain={'x': [0, 1], 'y': [0, 1]},
    gauge={'axis': {'range': [None, 100]}}
))

# Create a function to update plots and scores
def update_plots(selected_columns):
    consistency_scores = checker.calculate_consistency_scores(selected_columns)
    relevancy_scores = checker.calculate_relevancy_scores(selected_columns, 3)

    consistency_df = pd.DataFrame(consistency_scores)
    relevancy_df = pd.DataFrame(relevancy_scores)

    consistency_df["ConsistencyPercentage"] = (consistency_df["ConsistencyScore"] * 100).round(2)
    relevancy_df["RelevancyPercentage"] = ((relevancy_df["RelevancyScore"] / total_columns) * 100).round(2)

    fig_consistency.data = px.bar(consistency_df, x="Column", y="ConsistencyScore", title="Consistency Scores").data
    fig_relevancy.data = px.bar(relevancy_df, x="Column", y="RelevancyScore", title="Relevancy Scores").data
    circle_overall_consistency.data[0].value = (consistency_df["ConsistencyScore"].mean() * 100).round(2)
    circle_overall_relevancy.data[0].value = (relevancy_df["RelevancyScore"].sum() / (total_columns * len(data)) * 100).round(2)

# Create the layout
layout = pn.Column(
    "# Air Quality Data Quality Dashboard",
    column_dropdown,
    "## Overall Scores",
    pn.Row(
        pn.pane.Plotly(circle_overall_consistency),
        pn.pane.Plotly(circle_overall_relevancy)
    ),
    "## Consistency Scores",
    pn.pane.Plotly(fig_consistency),
    "## Relevancy Scores",
    pn.pane.Plotly(fig_relevancy)
)

# Link the dropdown widget to the update function
column_dropdown.link(update_plots, value='value')

# Display the layout
layout.servable()
