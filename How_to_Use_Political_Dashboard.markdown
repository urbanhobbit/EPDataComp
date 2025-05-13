# How to Use the Political Dashboard

This guide provides step-by-step instructions for setting up and using the Political Dashboard, a Streamlit application that visualizes citizens' priorities and political orientations in Europe based on data from `Data2Add.xlsx`.

## Overview

The Political Dashboard allows you to:
- View the most important societal issues in European countries.
- Explore political orientation distributions across countries.
- Compare issues and political orientations between two countries.
- Filter specific issues or orientations to display in charts.
- Toggle visibility of comparison charts.
- Download charts as PNG images and data tables as CSV files for further use.

The dashboard is built using Streamlit and Plotly, offering interactive charts and data tables for a comprehensive analysis.

## Prerequisites

Before using the dashboard, ensure you have the following:

1. **Python 3.8 or higher** installed on your system.
2. **Required Python packages**:
   - Install the necessary dependencies by running:
     ```
     pip install streamlit pandas plotly kaleido pillow
     ```
3. **Data File**:
   - Ensure the `Data2Add.xlsx` file is in the same directory as the script (`Command_fixed.py`). This file should contain two sheets:
     - `Most Im`: Data on the most important problems, with columns including "Most Important Problem" and country names.
     - `Sheet2`: Data on political orientations, with columns including "Left-Right Orientation" and country names.
4. **Optional Files**:
   - `Logo CO3.png`: A logo image for the dashboard header (optional; if missing, a text header will be used).
   - `styles.css`: A CSS file for custom styling (optional; default styles will be applied if missing).

## Setup and Running the Dashboard

1. **Save the Script**:
   - Save the script as `Command_fixed.py` in your working directory.

2. **Prepare the Data**:
   - Ensure `Data2Add.xlsx` is in the same directory as `Command_fixed.py`. The file must contain the required sheets and columns as described above.

3. **Run the Application**:
   - Open a terminal or command prompt in the directory containing the script.
   - Run the following command to start the Streamlit server:
     ```
     streamlit run Command_fixed.py
     ```
   - Your default web browser should automatically open to `http://localhost:8501`. If it doesn’t, open this URL manually.

## Using the Dashboard

The dashboard has four main views, accessible via the sidebar navigation. Each view displays charts and data tables, with options to filter data, toggle chart visibility, and download charts as PNG or CSV files.

### 1. Sidebar Navigation
- On the left side of the dashboard, you’ll see a sidebar with two sections: "Settings" and "Navigation".
- **Settings**:
  - Use the "Theme" radio buttons to switch between Light and Dark modes for better visibility.
- **Navigation**:
  - Use the radio buttons to switch between the following views:
    - **Most Important Problems**: View the top societal issues for a single country.
    - **Political Orientation**: Explore the political orientation distribution for a single country.
    - **Compare Countries**: Compare issues and political orientations between two countries.
    - **How to Use**: Access this guide for instructions on using the dashboard.

### 2. Most Important Problems View
- **Purpose**: Displays a bar chart of the most important societal issues for a selected country, along with a data table.
- **Steps**:
  1. Select a country from the dropdown menu (e.g., "EU27" or "Bulgaria").
  2. Use the multiselect widget to choose specific issues to display (e.g., "Rising prices, cost of living").
  3. View the chart showing the selected issues and their proportions (e.g., 36.0%).
  4. Below the chart, see a table listing the issues and their proportions in percentage format.
  5. Click the "📥 Download as PNG" link to save the chart as a PNG image (e.g., `EU27_top_issues.png`).
  6. Click the "📥 Download as CSV" link to save the table data as a CSV file (e.g., `EU27_top_issues.csv`).
- **Note**: To compare this country with another, switch to the "Compare Countries" view.

### 3. Political Orientation View
- **Purpose**: Shows a bar chart of the political orientation distribution (e.g., Left, Right) for a selected country, with a data table.
- **Steps**:
  1. Select a country from the dropdown menu.
  2. Use the multiselect widget to choose specific orientations to display (e.g., "Left", "Right").
  3. View the chart showing the selected political orientations and their proportions.
  4. Check the table below the chart for the exact proportions in percentage format.
  5. Click the "📥 Download as PNG" link to save the chart as a PNG image (e.g., `EU27_orientation.png`).
  6. Click the "📥 Download as CSV" link to save the table data as a CSV file (e.g., `EU27_orientation.csv`).

### 4. Compare Countries View
- **Purpose**: Compares the most important issues and political orientations between two countries in side-by-side charts and tables, with options to toggle chart visibility.
- **Steps**:
  1. Select the first country from the left dropdown menu.
  2. Select the second country from the right dropdown menu.
  3. Use the checkboxes to toggle visibility of the charts:
     - Check "Show Issues Comparison Chart" to display the issues comparison chart.
     - Check "Show Political Orientation Chart" to display the political orientation chart.
  4. **Issues Comparison**:
     - Use the multiselect widget to choose specific issues to compare.
     - View the grouped bar chart comparing the most important problems between the two countries.
     - Below the chart, see a table showing the data for both countries side by side in percentage format.
     - Download the chart as a PNG file (e.g., `EU27_Bulgaria_issues.png`) or the table as a CSV file (e.g., `EU27_Bulgaria_issues.csv`).
  5. **Political Orientation Comparison**:
     - Use the multiselect widget to choose specific orientations to compare.
     - View the grouped bar chart comparing political orientations between the two countries.
     - Below the chart, see a table showing the data for both countries side by side in percentage format.
     - Download the chart as a PNG file (e.g., `EU27_Bulgaria_orientation.png`) or the table as a CSV file (e.g., `EU27_Bulgaria_orientation.csv`).

### 5. How to Use View
- **Purpose**: Provides this guide to help you understand and navigate the dashboard.
- **Steps**:
  - Select the "How to Use" option in the sidebar navigation to view this guide.
  - Follow the instructions to set up, run, and use the dashboard features.

## Troubleshooting

- **Dashboard Doesn’t Load**:
  - Ensure `Data2Add.xlsx` is in the correct directory and contains the required sheets and columns.
  - Verify that all Python dependencies are installed (`streamlit`, `pandas`, `plotly`, `kaleido`, `pillow`).
- **Chart Doesn’t Update When Changing Country**:
  - If the chart shows data for the previous country, refresh the page to force a reload. This is a known issue being addressed in future updates.
- **PNG or CSV Download Fails**:
  - Ensure `kaleido` is installed and working (`pip install kaleido`).
  - If running on a hosted environment (e.g., Streamlit Cloud), ensure `kaleido` is included in your `requirements.txt`.
- **Charts Don’t Display**:
  - Check for errors in the terminal where Streamlit is running. Common issues include missing data columns or invalid data formats in `Data2Add.xlsx`.

## Additional Notes

- **Data Format**: Proportions in the data are normalized automatically. If the values in `Data2Add.xlsx` are in percentages (e.g., 36 for 36%), the dashboard converts them to decimals (0.36) for plotting and then displays them as percentages in tables.
- **Custom Styling**: You can customize the appearance by editing `styles.css`. If this file is missing, default styles are applied.
- **Logo**: Replace `Logo CO3.png` with your own logo image to personalize the dashboard header.

## Contact

For further assistance, contact the development team at Istanbul Bilgi University (2025 cohort).

---
*Last updated: May 13, 2025*