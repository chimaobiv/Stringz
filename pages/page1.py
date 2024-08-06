import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Explanation of Analysis
layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(
                dbc.Button("Back to Main Page", href="/", color="primary", className="mb-4"),
                width="auto"
            )
        ]),
        dbc.Row([
            dbc.Col(html.H1("Weather Analysis Overview"), className="mb-4")
        ]),
        dbc.Row([
            dbc.Col(
                html.P(
                    "This analysis provides insights into the weather patterns of various cities over a specified period. "
                    "We utilize temperature, humidity, wind speed, and other meteorological data to identify trends, correlations, "
                    "and extreme variations. The data is visualized using various plots to aid in understanding the relationships between different weather attributes."
                ),
                className="mb-4"
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.A(dbc.Button("Summary Analysis", color="primary"), href="/sub_page1a"),
                width="auto"
            ),
            dbc.Col(
                html.A(dbc.Button("Specific Analysis", color="primary"), href="/sub_page1b"),
                width="auto"
            )
        ])
    ],
    fluid=True
)


