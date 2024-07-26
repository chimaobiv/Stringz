from dash import dcc, html
import dash_bootstrap_components as dbc

index_layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(
                dbc.Button("Back to Main Page", href="/", color="primary", className="mb-4"),
                width=12
            )
        ]),
        html.H1("Fire Hazard Analysis", style={"color": "#2E4053", "font-family": "'Arial', sans-serif"}),
        html.P(
            [
                "The dataset used in this analysis is derived from NASA's Fire Information for Resource Management System (FIRMS), accessible at ",
                html.A("FIRMS MODIS and VIIRS Download", href="https://firms.modaps.eosdis.nasa.gov/download/", style={"color": "#3498DB"}),
                ". FIRMS provides global data on fire occurrences, brightness temperatures, and fire radiative power using data captured by the MODIS (Moderate Resolution Imaging Spectroradiometer) and VIIRS (Visible Infrared Imaging Radiometer Suite) instruments. The dataset contains information on fire occurrences captured by satellites. The key columns in the dataset include:"
            ],
            style={"font-family": "'Arial', sans-serif"}
        ),
        html.Ul(
            [
                html.Li([html.B("ACQ_DATE"), ": The date when the data was acquired."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("LATITUDE"), ": The latitude coordinate of the fire event."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("LONGITUDE"), ": The longitude coordinate of the fire event."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("BRIGHTNESS"), ": The brightness temperature measured by the satellite."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("SCAN"), ": The width of the scan swath in kilometers."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("TRACK"), ": The along-track scan in kilometers."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("ACQ_TIME"), ": The time of data acquisition."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("SATELLITE"), ": The satellite that captured the data (e.g., Terra, Aqua)."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("INSTRUMENT"), ": The instrument used for data acquisition (e.g., MODIS, VIIRS)."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("CONFIDENCE"), ": The confidence level of the fire detection."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("VERSION"), ": The version of the dataset."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("BRIGHT_T31"), ": The brightness temperature at 31 micrometers."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("FRP"), ": Fire Radiative Power, indicating the energy released by the fire."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("DAYNIGHT"), ": Indicates whether the detection was during day or night."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("TYPE"), ": Type of fire event."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("GEOMETRY"), ": Geographic coordinates in point format."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("YEAR"), ": The year when the data was acquired."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("MONTH"), ": The month when the data was acquired."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("SEASON"), ": The season when the data was acquired."], style={"font-family": "'Arial', sans-serif"}),
                html.Li([html.B("REGION"), ": The geographic region where the fire occurred."], style={"font-family": "'Arial', sans-serif"})
            ]
        ),
        html.Hr(style={"border": "1px solid #2E4053"}),
        html.H2("Summary of Analysis", style={"color": "#2E4053", "font-family": "'Arial', sans-serif"}),
        html.H3("Fire Intensity and Magnitude", style={"color": "#1F618D", "font-family": "'Arial', sans-serif"}),
        html.Ul(
            [
                html.Li(
                    [html.B("Histograms"), ": Displayed the distribution of brightness temperatures (", html.B("BRIGHTNESS"), ") and Fire Radiative Power (", html.B("FRP"), ") to understand fire intensity variations."],
                    style={"font-family": "'Arial', sans-serif"}
                ),
                html.Li(
                    [html.B("Scatter Plots"), ": Compared brightness temperature with ", html.B("FRP"), " to explore the relationship between fire intensity and energy release."],
                    style={"font-family": "'Arial', sans-serif"}
                )
            ]
        ),
        html.H3("Temporal Trends", style={"color": "#1F618D", "font-family": "'Arial', sans-serif"}),
        html.H4("Monthly Fire Occurrences", style={"color": "#2874A6", "font-family": "'Arial', sans-serif"}),
        html.Ul(
            [html.Li("Analyzed fire occurrences by month for specific years to identify seasonal patterns and compare fire activity across different years.", style={"font-family": "'Arial', sans-serif"})]
        ),
        html.H4("Yearly Fire Trends", style={"color": "#2874A6", "font-family": "'Arial', sans-serif"}),
        html.Ul(
            [html.Li("Aggregated fire occurrences by year and plotted the data to observe long-term trends.", style={"font-family": "'Arial', sans-serif"})]
        ),
        html.H3("Fire Data Across Regions", style={"color": "#1F618D", "font-family": "'Arial', sans-serif"}),
        html.H4("Categorization by Region", style={"color": "#2874A6", "font-family": "'Arial', sans-serif"}),
        html.Ul(
            [html.Li("Divided the data into regions based on geographic coordinates.", style={"font-family": "'Arial', sans-serif"})]
        ),
        html.H4("Comparison", style={"color": "#2874A6", "font-family": "'Arial', sans-serif"}),
        html.Ul(
            [html.Li("Compared the number of fires, average brightness temperature, and average FRP across different regions.", style={"font-family": "'Arial', sans-serif"})]
        ),
        html.H3("Predicting Fire Occurrences", style={"color": "#1F618D", "font-family": "'Arial', sans-serif"}),
        html.H4("Modeling Approach", style={"color": "#2874A6", "font-family": "'Arial', sans-serif"}),
        html.Ul(
            [html.Li("Used a Random Forest Classifier to predict fire occurrences based on features such as geographic coordinates, brightness temperature, and environmental conditions.", style={"font-family": "'Arial', sans-serif"})]
        ),
        html.H4("Class Imbalance Handling", style={"color": "#2874A6", "font-family": "'Arial', sans-serif"}),
        html.Ul(
            [html.Li("Applied SMOTE (Synthetic Minority Over-sampling Technique) to balance the dataset and improve the model's performance on the minority class.", style={"font-family": "'Arial', sans-serif"})]
        ),
        html.H3("Model Evaluation", style={"color": "#1F618D", "font-family": "'Arial', sans-serif"}),
        html.H4("Initial Model", style={"color": "#2874A6", "font-family": "'Arial', sans-serif"}),
        html.Ul(
            [html.Li("Showed very high accuracy but poor performance on the minority class due to class imbalance.", style={"font-family": "'Arial', sans-serif"})]
        ),
        html.H4("Improved Model with SMOTE", style={"color": "#2874A6", "font-family": "'Arial', sans-serif"}),
        html.Ul(
            [html.Li("Achieved a better balance between precision and recall for the minority class while maintaining high overall accuracy.", style={"font-family": "'Arial', sans-serif"})]
        ),
        dbc.Button("Summary Analysis", href="/sub_page3a", color="primary", className="mt-3"),
        dbc.Button("Specific Analysis", href="/sub_page3b", color="primary", className="mt-3 ml-2")
    ],
    fluid=True
)
