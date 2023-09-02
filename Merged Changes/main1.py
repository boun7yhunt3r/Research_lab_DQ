##import data_quality as dq
import panel as pn
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.request
from zipfile import ZipFile
from importlib import reload
import matplotlib as plt

from Framework.data_quality import DataQualityChecker
from Framework.improve_dq import Improve_DQ


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

improver = Improve_DQ(data)

value =  checker.check_missing_data()
print(value)

# Add expectations and calculate scores
Consistency_scores = checker.calculate_consistency_scores(columns_of_interest)
Relevancy_scores = checker.calculate_relevancy_scores(columns_of_interest, 3)

# Create placeholders for overall data quality indicators
missing_count_pane = pn.pane.Str("")
completeness_pane = pn.pane.Str("")
stationarity_pane = pn.pane.Str("")
skewness_pane = pn.pane.Str("")

def update_overall_indicators(event):
    missing_count = checker.check_missing_count()
    stationarity_results = checker.calculate_stationarity()
    completeness = checker.calculate_completeness()
    skewness_results = checker.calculate_skewness()
   
    
    

    # Display the results in the dashboard
    missing_count_pane.object = f"<b>Missing Count:</b> {missing_count}"


   
    # Format stationarity results as a string
    stationarity_str = "<b>Stationary reults of the columns:</b>\n"+"\n".join([f"{col}: {'Stationary' if is_stationary else 'Non-Stationary'}" for col, is_stationary in stationarity_results.items()])
    stationarity_pane.object = stationarity_str  # Assign the formatted string

    completeness_pane.object = f"<b>Completeness:</b> {completeness}%"
    
    # Format skewness results as a string without decimal formatting
    skewness_str = "<b>Skewness of the columns:</b>\n" + "\n".join([f"{col}: {skew}" for col, skew in skewness_results.items()])
    skewness_pane.object = skewness_str  # Assign the formatted string
   


# Link a button widget to the update_overall_indicators function
update_button = pn.widgets.Button(name="Update Overall Indicators")
update_button.on_click(update_overall_indicators)


# Define columns of interest
all_columns = data.columns.tolist()

# Create interactive dropdown for selecting columns
column_dropdown = pn.widgets.MultiChoice(
    name="Select Columns of Interest",
    options=all_columns
)


# Create placeholders for the plots, indicators, and stationarity results
fig_consistency = pn.pane.Plotly()
fig_relevancy = pn.pane.Plotly()
circle_overall_consistency = pn.pane.Plotly()
circle_overall_relevancy = pn.pane.Plotly()


# Create a function to update plots and scores
def update_plots(event):
    selected_columns = column_dropdown.value
    selected_columns = [col for col in selected_columns if pd.api.types.is_numeric_dtype(data[col])]

    consistency_scores = checker.calculate_consistency_scores(selected_columns)
    relevancy_scores = checker.calculate_relevancy_scores(selected_columns, 3)

    consistency_df = pd.DataFrame(consistency_scores, columns=["Column", "ConsistencyScore"])
    relevancy_df = pd.DataFrame(relevancy_scores, columns=["Column", "RelevancyScore"])

    consistency_df["ConsistencyPercentage"] = ((consistency_df["ConsistencyScore"] / len(selected_columns)) * 100).round(2)
    relevancy_df["RelevancyPercentage"] = ((relevancy_df["RelevancyScore"] / len(selected_columns)) * 100).round(2)

    fig_consistency.object = px.bar(consistency_df, x="Column", y="ConsistencyScore", title="Consistency Scores")
    fig_relevancy.object = px.bar(relevancy_df, x="Column", y="RelevancyScore", title="Relevancy Scores")

    overall_normalized_consistency = checker.calculate_overall_normalized_consistency(selected_columns)
    overall_normalized_relevancy = checker.calculate_overall_normalized_relevancy(selected_columns, outlier_threshold=3)

    circle_overall_consistency.object = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_normalized_consistency,
        title="Overall Normalized Consistency",
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 1]}}  # Normalize between 0 and 1
    ))

    circle_overall_relevancy.object = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_normalized_relevancy,
        title="Overall Normalized Relevancy",
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 1]}}  # Normalize between 0 and 1
    ))

    # Calculate and display time shifts for selected columns
    time_shift_results = checker.calculate_time_shifts(selected_columns)
    time_shifts_text = "\nTime Shifts:\n"
    for column, time_shift in time_shift_results.items():
        time_shifts_text += f"{column}: {time_shift}\n"
    time_shifts_pane.object = time_shifts_text
    

# Link the dropdown widget to the update function
column_dropdown.param.watch(update_plots, "value")
time_shifts_pane = pn.pane.Str("")  # Initialize with an empty string

# Create the layout
layout = pn.Column(
    "# Air Quality Data Quality Dashboard",
    update_button,
    "## Overall Data Quality Indicators",
    missing_count_pane,
    completeness_pane,
    skewness_pane,
    stationarity_pane,
    column_dropdown,
    "## Overall Scores",
    pn.Row(
        circle_overall_consistency,
        circle_overall_relevancy
    ),
    "## Consistency Scores",
    fig_consistency,
    "## Relevancy Scores",
    fig_relevancy,
    "## Time Shifts",  # Add a section for displaying time shifts
    time_shifts_pane  # Add the time shifts pane
)
# Display the layout
layout.servable()



