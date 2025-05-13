import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import base64
from PIL import Image
import plotly.io as pio
from pathlib import Path
import time

# Set page config as the first Streamlit command
st.set_page_config(layout="wide", page_title="Political Dashboard", page_icon="📊")

# Ensure Kaleido is set for PNG export
pio.kaleido.scope.default_format = "png"

class PoliticalDashboard:
    """A class to manage the Political Dashboard application using Streamlit."""
    
    def __init__(self):
        """Initialize the dashboard with configuration and data."""
        # Configuration
        self.DATA_FILE = "Data2Add.xlsx"
        self.LOGO_PATH = "Logo CO3.png"
        self.CSS_PATH = "styles.css"
        
        # Load data
        self.df_most_im, self.df_sheet2 = PoliticalDashboard._load_data()
        self.countries = PoliticalDashboard._get_common_countries(self.df_most_im, self.df_sheet2)
        
        # Initialize session state for theme, filters, and country tracking
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
        if 'selected_issues' not in st.session_state:
            st.session_state.selected_issues = list(self.df_most_im["Most Important Problem"])
        if 'selected_orientations' not in st.session_state:
            st.session_state.selected_orientations = list(self.df_sheet2["Left-Right Orientation"])
        if 'show_issues_chart' not in st.session_state:
            st.session_state.show_issues_chart = True
        if 'show_orientation_chart' not in st.session_state:
            st.session_state.show_orientation_chart = True
        if 'last_country_mip' not in st.session_state:
            st.session_state.last_country_mip = None
        if 'last_country_po' not in st.session_state:
            st.session_state.last_country_po = None

    @staticmethod
    @st.cache_data
    def _load_data():
        """Load and validate data from the Excel file."""
        try:
            data_path = Path("Data2Add.xlsx")
            df_most_im = pd.read_excel(data_path, sheet_name="Most Im")
            df_sheet2 = pd.read_excel(data_path, sheet_name="Sheet2")
            
            # Validate required columns
            if "Most Important Problem" not in df_most_im.columns:
                st.error("Error: Required column 'Most Important Problem' missing in 'Most Im' sheet.")
                st.stop()
            if "Left-Right Orientation" not in df_sheet2.columns:
                st.error("Error: Required column 'Left-Right Orientation' missing in 'Sheet2' sheet.")
                st.stop()
                
            # Clean data
            df_most_im = df_most_im.dropna(axis=1, how='all')
            df_sheet2 = df_sheet2.dropna(axis=1, how='all')
            
            # Normalize proportions
            for col in df_most_im.columns[1:]:
                if df_most_im[col].max() > 1:  # Assume percentages if max > 1
                    df_most_im[col] = df_most_im[col] / 100
            for col in df_sheet2.columns[1:]:
                if df_sheet2[col].max() > 1:  # Assume percentages if max > 1
                    df_sheet2[col] = df_sheet2[col] / 100
            
            return df_most_im, df_sheet2
        except FileNotFoundError:
            st.error(f"Error: 'Data2Add.xlsx' not found. Please ensure the file exists.")
            st.stop()
        except ValueError as e:
            st.error(f"Error: Invalid sheet names or file structure. Details: {e}")
            st.stop()

    @staticmethod
    def _get_common_countries(df_most_im, df_sheet2):
        """Get a sorted list of countries common to both datasets."""
        countries = sorted(list(set(df_most_im.columns[1:]).intersection(set(df_sheet2.columns[1:]))))
        if not countries:
            st.error("Error: No common countries found between the two sheets.")
            st.stop()
        return countries

    def _apply_chart_styling(self, fig, title):
        """Apply consistent styling to Plotly charts."""
        fig.update_layout(
            title={"text": title, "x": 0.5, "xanchor": "center"},
            showlegend=True,
            plot_bgcolor='#FFFFFF' if st.session_state.theme == 'light' else '#333333',
            paper_bgcolor='#FFFFFF' if st.session_state.theme == 'light' else '#333333',
            font=dict(family="Arial", size=12, color='#000000' if st.session_state.theme == 'light' else '#FFFFFF'),
            xaxis_tickformat='.0%',
            template="plotly_white" if st.session_state.theme == 'light' else "plotly_dark"
        )
        fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')
        return fig

    def _get_image_download_link(self, fig, filename):
        """Generate a download link for a Plotly chart as a PNG image."""
        try:
            buffer = BytesIO()
            fig.write_image(buffer, format='png')
            buffer.seek(0)
            b64 = base64.b64encode(buffer.read()).decode()
            return f'<a href="data:file/png;base64,{b64}" download="{filename}" role="button" aria-label="Download {filename}">📥 Download as PNG</a>'
        except Exception as e:
            st.error(f"Failed to generate download link: {str(e)}")
            return None

    def _get_csv_download_link(self, df, filename):
        """Generate a download link for a DataFrame as a CSV file."""
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=True)
        csv_buffer.seek(0)
        b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        return f'<a href="data:file/csv;base64,{b64}" download="{filename}" role="button" aria-label="Download {filename}">📥 Download as CSV</a>'

    def _get_excel_download_link(self, filename):
        """Generate a download link for the full dataset as an Excel file."""
        try:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                self.df_most_im.to_excel(writer, sheet_name="Most Im", index=False)
                self.df_sheet2.to_excel(writer, sheet_name="Sheet2", index=False)
            buffer.seek(0)
            b64 = base64.b64encode(buffer.getvalue()).decode()
            return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" role="button" aria-label="Download {filename}">📥 Download Full Dataset as Excel</a>'
        except Exception as e:
            st.error(f"Failed to generate Excel download link: {str(e)}")
            return None

    @staticmethod
    def _create_most_important_chart(df, country, selected_issues, _cache_buster):
        """Create a bar chart for the most important problems in a country."""
        st.write(f"Debug: Generating chart for country: {country}")
        filtered_df = df[df["Most Important Problem"].isin(selected_issues)]
        fig = px.bar(filtered_df, x=country, y='Most Important Problem', orientation='h',
                     labels={country: "Proportion", 'Most Important Problem': "Issue"},
                     text=country, color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Proportion')
        return fig, filtered_df

    @staticmethod
    def _create_political_orientation_chart(df, country, selected_orientations, _cache_buster):
        """Create a bar chart for political orientation distribution in a country."""
        st.write(f"Debug: Generating chart for country: {country}")
        filtered_df = df[df["Left-Right Orientation"].isin(selected_orientations)]
        data = filtered_df[["Left-Right Orientation", country]].rename(columns={country: "Proportion"})
        fig = px.bar(data, x="Left-Right Orientation", y="Proportion",
                     color="Left-Right Orientation", text="Proportion",
                     color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_layout(yaxis_title='Proportion')
        return fig, data

    @staticmethod
    @st.cache_data
    def _create_comparison_issues_chart(df, country1, country2, selected_issues):
        """Create a comparison bar chart for issues between two countries."""
        filtered_df = df[df["Most Important Problem"].isin(selected_issues)]
        compare_df = filtered_df[["Most Important Problem", country1, country2]].melt(
            id_vars="Most Important Problem", var_name="Country", value_name="Proportion")
        fig = px.bar(compare_df, x="Proportion", y="Most Important Problem",
                     color="Country", barmode="group", orientation='h',
                     text="Proportion", color_discrete_sequence=px.colors.qualitative.Plotly[:2])
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Proportion')
        
        for issue in filtered_df["Most Important Problem"]:
            prop1 = filtered_df[filtered_df["Most Important Problem"] == issue][country1].iloc[0]
            prop2 = filtered_df[filtered_df["Most Important Problem"] == issue][country2].iloc[0]
            if abs(prop1 - prop2) > 0.1:
                fig.add_annotation(
                    x=0.5, y=issue,
                    text="⚠️ Significant difference",
                    showarrow=False, xref="paper", yref="y",
                    font=dict(size=10, color="red"),
                    align="left"
                )
        
        return fig, compare_df

    @staticmethod
    @st.cache_data
    def _create_comparison_orientation_chart(df, country1, country2, selected_orientations):
        """Create a comparison bar chart for political orientations between two countries."""
        filtered_df = df[df["Left-Right Orientation"].isin(selected_orientations)]
        pol_df = filtered_df[["Left-Right Orientation", country1, country2]].melt(
            id_vars="Left-Right Orientation", var_name="Country", value_name="Proportion")
        fig = px.bar(pol_df, x="Left-Right Orientation", y="Proportion",
                     color="Country", barmode="group", text="Proportion",
                     color_discrete_sequence=px.colors.qualitative.Plotly[:2])
        fig.update_layout(yaxis_title='Proportion')
        return fig, pol_df

    def _render_styles(self):
        """Apply custom styles based on the selected theme."""
        css_path = Path(self.CSS_PATH)
        if css_path.exists():
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            if st.session_state.theme == 'light':
                st.markdown("""
                    <style>
                    .stApp {
                        background-color: #F5F5F5;
                        color: #333333;
                    }
                    .main > div {
                        padding: 1rem;
                        font-size: 1.15rem;
                        background-color: #FFFFFF;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    h1, h2, h3 {
                        color: #004080;
                    }
                    .sidebar .sidebar-content {
                        background-color: #FFFFFF;
                        padding: 1rem;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    hr {
                        border-color: #D3D3D3;
                    }
                    .stButton > button {
                        background-color: #004080;
                        color: #FFFFFF;
                        border-radius: 4px;
                    }
                    .stButton > button:hover {
                        background-color: #1f77b4;
                    }
                    </style>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <style>
                    .stApp {
                        background-color: #1E1E1E;
                        color: #D3D3D3;
                    }
                    .main > div {
                        padding: 1rem;
                        font-size: 1.15rem;
                        background-color: #2A2A2A;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    }
                    h1, h2, h3 {
                        color: #66B2FF;
                    }
                    .sidebar .sidebar-content {
                        background-color: #2A2A2A;
                        padding: 1rem;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    }
                    hr {
                        border-color: #555555;
                    }
                    .stButton > button {
                        background-color: #66B2FF;
                        color: #000000;
                        border-radius: 4px;
                    }
                    .stButton > button:hover {
                        background-color: #99CCFF;
                    }
                    </style>
                """, unsafe_allow_html=True)

    def _render_header(self):
        """Render the dashboard header with logo and title."""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if Path(self.LOGO_PATH).exists():
                st.image(self.LOGO_PATH, width=140)
            else:
                st.markdown("<h3 style='text-align: center;'>Political Dashboard</h3>", unsafe_allow_html=True)
        st.markdown("## 📊 Political Dashboard")
        st.markdown("### Understanding Citizens' Priorities and Political Orientations in Europe")
        st.markdown("This dashboard provides insights into societal issues and political alignment across Europe.")

    def _render_how_to_use(self):
        """Render the 'How to Use' view with the user guide."""
        st.markdown("""
            # How to Use the Political Dashboard

            This guide provides step-by-step instructions for setting up and using the Political Dashboard, a Streamlit application that visualizes citizens' priorities and political orientations in Europe based on data from `Data2Add.xlsx`.

            ## Overview

            The Political Dashboard allows you to:
            - View the most important societal issues in European countries.
            - Explore political orientation distributions across countries.
            - Compare issues and political orientations between two countries.
            - Filter specific issues or orientations to display in charts.
            - Toggle visibility of comparison charts.
            - Download charts as PNG images, data tables as CSV files, or the full dataset as an Excel file for further use.

            The dashboard is built using Streamlit and Plotly, offering interactive charts and data tables for a comprehensive analysis. It is deployed on Streamlit Community Cloud, making it accessible online without local setup.

            ## Accessing the Deployed App

            The Political Dashboard is hosted on Streamlit Community Cloud and can be accessed directly at the following URL:
            - **App URL**: [Insert your app URL here, e.g., `https://political-dashboard-2025.streamlit.app`]

            Simply open the URL in your web browser to start using the dashboard. No local setup is required to access the deployed version. If you’d like to run the app locally for development or customization, follow the setup instructions below.

            ## Prerequisites (For Local Setup)

            If you want to run the app locally (e.g., for development or offline use), ensure you have the following:

            1. **Python 3.8 or higher** installed on your system.
            2. **Required Python packages**:
               - Install the necessary dependencies by running:
                 ```
                 pip install streamlit pandas plotly kaleido pillow xlsxwriter openpyxl
                 ```
            3. **Data File**:
               - Ensure the `Data2Add.xlsx` file is in the same directory as the script (`Command_fixed.py`). This file should contain two sheets:
                 - `Most Im`: Data on the most important problems, with columns including "Most Important Problem" and country names.
                 - `Sheet2`: Data on political orientations, with columns including "Left-Right Orientation" and country names.
            4. **Optional Files**:
               - `Logo CO3.png`: A logo image for the dashboard header (optional; if missing, a text header will be used).
               - `styles.css`: A CSS file for custom styling (optional; default styles will be applied if missing).

            ## Setup and Running the Dashboard Locally

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

            The dashboard has four main views, accessible via the sidebar navigation. Each view displays charts and data tables, with options to filter data, toggle chart visibility, and download charts as PNG or CSV files. Additionally, you can export the full dataset from the sidebar.

            ### 1. Sidebar Navigation
            - On the left side of the dashboard, you’ll see a sidebar with two sections: "Settings" and "Navigation".
            - **Settings**:
              - Use the "Theme" radio buttons to switch between Light and Dark modes for better visibility.
              - Click the "Export Full Dataset" button to download the complete dataset (`Most Im` and `Sheet2` sheets) as an Excel file (`political_dashboard_data.xlsx`).
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
              - Ensure `Data2Add.xlsx` is in the correct directory and contains the required sheets and columns (for local setup).
              - Verify that all Python dependencies are installed (`streamlit`, `pandas`, `plotly`, `kaleido`, `pillow`, `xlsxwriter`, `openpyxl`).
              - For the deployed app, check the Streamlit Community Cloud logs for errors (accessible via your workspace at `share.streamlit.io`).
            - **Chart Doesn’t Update When Changing Country**:
              - If the chart shows data for the previous country, refresh the page to force a reload. This is a known issue being addressed in future updates.
            - **PNG, CSV, or Excel Download Fails**:
              - Ensure `kaleido` is installed for PNG downloads (`pip install kaleido`).
              - Ensure `xlsxwriter` is installed for Excel exports (`pip install xlsxwriter`).
              - Ensure `openpyxl` is installed for reading Excel files (`pip install openpyxl`).
              - If running on Streamlit Community Cloud, ensure `kaleido`, `xlsxwriter`, and `openpyxl` are listed in `requirements.txt`.
            - **Charts Don’t Display**:
              - Check for errors in the terminal (local setup) or Streamlit Cloud logs (deployed app). Common issues include missing data columns or invalid data formats in `Data2Add.xlsx`.

            ## Additional Notes

            - **Data Format**: Proportions in the data are normalized automatically. If the values in `Data2Add.xlsx` are in percentages (e.g., 36 for 36%), the dashboard converts them to decimals (0.36) for plotting and then displays them as percentages in tables.
            - **Custom Styling**: You can customize the appearance by editing `styles.css`. If this file is missing, default styles are applied.
            - **Logo**: Replace `Logo CO3.png` with your own logo image to personalize the dashboard header.
            - **Deployed App Limitations**: The app is hosted on Streamlit Community Cloud’s free tier, which has resource limits (e.g., memory, CPU usage). If the app slows down or becomes nonfunctional, it may have exceeded these limits. Consider applying for increased resources if your app is for educational or nonprofit use.

            ## Contact

            For further assistance, contact the development team at Istanbul Bilgi University (2025 cohort).

            ---
            *Last updated: May 13, 2025*
        """, unsafe_allow_html=True)

    def run(self):
        """Run the dashboard application."""
        # Apply styles
        self._render_styles()
        
        # Sidebar: Theme toggle, export button, and navigation
        st.sidebar.header("Settings")
        theme = st.sidebar.radio("Theme", ["Light", "Dark"], index=0 if st.session_state.theme == 'light' else 1)
        st.session_state.theme = 'light' if theme == "Light" else 'dark'
        
        # Export full dataset button
        if st.sidebar.button("Export Full Dataset"):
            st.sidebar.markdown("Exporting the full dataset as an Excel file...")
            download_link = self._get_excel_download_link("political_dashboard_data.xlsx")
            if download_link:
                st.sidebar.markdown(download_link, unsafe_allow_html=True)
                st.sidebar.success("Full dataset exported successfully!")
        
        st.sidebar.header("Navigation")
        page = st.sidebar.radio("Select a view:", ["Most Important Problems", "Political Orientation", "Compare Countries", "How to Use"], label_visibility="collapsed")
        
        # Render header
        self._render_header()
        
        # Page logic
        with st.container():
            if page == "Most Important Problems":
                self._render_most_important_problems()
            elif page == "Political Orientation":
                self._render_political_orientation()
            elif page == "Compare Countries":
                self._render_compare_countries()
            elif page == "How to Use":
                self._render_how_to_use()
        
        # Footer
        st.markdown("""
            <hr style='margin-top: 3rem; border-color: #D3D3D3;'>
            <p style='text-align: center; font-size: 0.9rem; color: #333333;'>
                Developed by <strong>Istanbul Bilgi University Team - 2025</strong><br>
                Powered by Streamlit & Plotly
            </p>
        """, unsafe_allow_html=True)

    def _render_most_important_problems(self):
        """Render the 'Most Important Problems' view."""
        country = st.selectbox("Select a country:", self.countries, key="mip_country", help="Choose a country to view its top issues.")
        st.session_state.selected_issues = st.multiselect("Select issues to display:", list(self.df_most_im["Most Important Problem"]),
                                                         default=st.session_state.selected_issues, key="mip_issues")
        
        if not st.session_state.selected_issues:
            st.warning("Please select at least one issue to display.")
            return
        
        # Check if country has changed and reset chart if necessary
        if st.session_state.last_country_mip != country:
            st.session_state.last_country_mip = country
            st.write(f"Debug: Country changed to {country}, regenerating chart...")
        
        flag = "🇪🇺" if country == "EU27" else ""
        st.markdown(f"### {flag} Most Important Problems in **{country}**")
        
        # Use a unique cache buster to force chart regeneration
        cache_buster = f"{country}_{time.time()}"
        with st.spinner("Generating chart..."):
            fig, filtered_df = PoliticalDashboard._create_most_important_chart(self.df_most_im, country, st.session_state.selected_issues, cache_buster)
            fig = self._apply_chart_styling(fig, f"Top Issues in {country}")
            st.plotly_chart(fig, use_container_width=True, key=f"mip_chart_{country}")
        
        download_link = self._get_image_download_link(fig, f"{country}_top_issues.png")
        if download_link:
            st.markdown(download_link, unsafe_allow_html=True)
        
        # Display data table
        st.markdown("#### Data Table")
        table_data = filtered_df[["Most Important Problem", country]].copy()
        table_data[country] = table_data[country].apply(lambda x: f"{x*100:.1f}%")
        st.dataframe(table_data, use_container_width=True)
        
        # CSV download
        csv_link = self._get_csv_download_link(table_data, f"{country}_top_issues.csv")
        if csv_link:
            st.markdown(csv_link, unsafe_allow_html=True)
        
        st.info("ℹ️ To compare this country with another, please use the **Compare Countries** view in the sidebar.")

    def _render_political_orientation(self):
        """Render the 'Political Orientation' view."""
        country = st.selectbox("Select a country:", self.countries, key="po_country", help="Choose a country to view its political orientation.")
        st.session_state.selected_orientations = st.multiselect("Select orientations to display:", list(self.df_sheet2["Left-Right Orientation"]),
                                                               default=st.session_state.selected_orientations, key="po_orientations")
        
        if not st.session_state.selected_orientations:
            st.warning("Please select at least one orientation to display.")
            return
        
        # Check if country has changed and reset chart if necessary
        if st.session_state.last_country_po != country:
            st.session_state.last_country_po = country
            st.write(f"Debug: Country changed to {country}, regenerating chart...")
        
        st.markdown(f"### 🧭 Political Orientation in **{country}**")
        
        # Use a unique cache buster to force chart regeneration
        cache_buster = f"{country}_{time.time()}"
        with st.spinner("Generating chart..."):
            fig, data = PoliticalDashboard._create_political_orientation_chart(self.df_sheet2, country, st.session_state.selected_orientations, cache_buster)
            fig = self._apply_chart_styling(fig, f"Political Orientation in {country}")
            st.plotly_chart(fig, use_container_width=True, key=f"po_chart_{country}")
        
        download_link = self._get_image_download_link(fig, f"{country}_orientation.png")
        if download_link:
            st.markdown(download_link, unsafe_allow_html=True)
        
        # Display data table
        st.markdown("#### Data Table")
        table_data = data.copy()
        table_data["Proportion"] = table_data["Proportion"].apply(lambda x: f"{x*100:.1f}%")
        st.dataframe(table_data, use_container_width=True)
        
        # CSV download
        csv_link = self._get_csv_download_link(table_data, f"{country}_orientation.csv")
        if csv_link:
            st.markdown(csv_link, unsafe_allow_html=True)

    def _render_compare_countries(self):
        """Render the 'Compare Countries' view with toggles for charts."""
        default_country1, default_country2 = self.countries[:2] if len(self.countries) >= 2 else (self.countries[0], self.countries[0])
        col1, col2 = st.columns([1, 1])
        with col1:
            country1 = st.selectbox("First country:", self.countries, index=self.countries.index(default_country1), key="c1", help="Select the first country for comparison.")
        with col2:
            country2 = st.selectbox("Second country:", self.countries, index=self.countries.index(default_country2), key="c2", help="Select the second country for comparison.")
        
        # Toggle for showing/hiding charts
        st.session_state.show_issues_chart = st.checkbox("Show Issues Comparison Chart", value=st.session_state.show_issues_chart, key="show_issues")
        st.session_state.show_orientation_chart = st.checkbox("Show Political Orientation Chart", value=st.session_state.show_orientation_chart, key="show_orientation")

        # Issues comparison
        with st.container():
            st.markdown("---")  # Separator
            st.session_state.selected_issues = st.multiselect("Select issues to compare:", list(self.df_most_im["Most Important Problem"]),
                                                             default=st.session_state.selected_issues, key="cc_issues")
            
            if not st.session_state.selected_issues:
                st.warning("Please select at least one issue to compare.")
            elif st.session_state.show_issues_chart:
                st.markdown(f"### 🔍 Comparing Issues: **{country1}** vs **{country2}**")
                with st.spinner("Generating issues chart..."):
                    fig1, compare_df = PoliticalDashboard._create_comparison_issues_chart(self.df_most_im, country1, country2, st.session_state.selected_issues)
                    fig1 = self._apply_chart_styling(fig1, f"Issue Importance: {country1} vs {country2}")
                    st.plotly_chart(fig1, use_container_width=True, key=f"cc_issues_chart_{country1}_{country2}")
                download_link = self._get_image_download_link(fig1, f"{country1}_{country2}_issues.png")
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)
                
                # Display data table
                st.markdown("#### Data Table")
                table_data = compare_df.pivot(index="Most Important Problem", columns="Country", values="Proportion")
                table_data = table_data.applymap(lambda x: f"{x*100:.1f}%")
                st.dataframe(table_data, use_container_width=True)
                
                # CSV download
                csv_link = self._get_csv_download_link(table_data, f"{country1}_{country2}_issues.csv")
                if csv_link:
                    st.markdown(csv_link, unsafe_allow_html=True)
        
        # Political orientation comparison
        with st.container():
            st.markdown("---")  # Separator
            st.session_state.selected_orientations = st.multiselect("Select orientations to compare:", list(self.df_sheet2["Left-Right Orientation"]),
                                                                   default=st.session_state.selected_orientations, key="cc_orientations")
            
            if not st.session_state.selected_orientations:
                st.warning("Please select at least one orientation to compare.")
            elif st.session_state.show_orientation_chart:
                st.markdown(f"### 🧭 Political Orientation: **{country1}** vs **{country2}**")
                with st.spinner("Generating orientation chart..."):
                    fig2, pol_df = PoliticalDashboard._create_comparison_orientation_chart(self.df_sheet2, country1, country2, st.session_state.selected_orientations)
                    fig2 = self._apply_chart_styling(fig2, f"Political Orientation: {country1} vs {country2}")
                    st.plotly_chart(fig2, use_container_width=True, key=f"cc_orientation_chart_{country1}_{country2}")
                download_link = self._get_image_download_link(fig2, f"{country1}_{country2}_orientation.png")
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)
                
                # Display data table
                st.markdown("#### Data Table")
                table_data = pol_df.pivot(index="Left-Right Orientation", columns="Country", values="Proportion")
                table_data = table_data.applymap(lambda x: f"{x*100:.1f}%")
                st.dataframe(table_data, use_container_width=True)
                
                # CSV download
                csv_link = self._get_csv_download_link(table_data, f"{country1}_{country2}_orientation.csv")
                if csv_link:
                    st.markdown(csv_link, unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard = PoliticalDashboard()
    dashboard.run()
