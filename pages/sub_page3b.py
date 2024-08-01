import gc
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables directly
api_key = os.getenv('tomtom_api_key')
mapbox_access_token = os.getenv('mapbox_access_token')


# Function to log memory usage
def log_memory_usage():
    import psutil
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    print(f"Memory Usage: RSS={mem_info.rss / 1024 ** 2:.2f} MB, VMS={mem_info.vms / 1024 ** 2:.2f} MB")


# Function to load data from SQLite
def load_data_from_sqlite(query):
    conn = sqlite3.connect('data/fire_archive_M-C61_490372.db')
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# Define the layout
layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(
                dbc.Button("Back to Main Page", href="/page3", color="primary", className="mb-4"),
                width=12
            )
        ]),
        html.H3("Analyze Specific Year and Month"),
        dcc.Dropdown(
            id='specific-year-dropdown',
            options=[],  # Will be populated dynamically
            placeholder="Select Year"
        ),
        dcc.Dropdown(
            id='specific-month-dropdown',
            options=[
                {'label': 'January', 'value': 1}, {'label': 'February', 'value': 2},
                {'label': 'March', 'value': 3}, {'label': 'April', 'value': 4},
                {'label': 'May', 'value': 5}, {'label': 'June', 'value': 6},
                {'label': 'July', 'value': 7}, {'label': 'August', 'value': 8},
                {'label': 'September', 'value': 9}, {'label': 'October', 'value': 10},
                {'label': 'November', 'value': 11}, {'label': 'December', 'value': 12}
            ],
            placeholder="Select Month"
        ),
        dbc.Button("Analyze", id="analyze-button", color="primary", className="mt-2"),
        dcc.Graph(id='specific_analysis'),
        html.H3("Temporal Trends for Specific Years"),
        dcc.Dropdown(
            id='specific-years-dropdown',
            options=[],  # Will be populated dynamically
            multi=True,
            placeholder="Select Years"
        ),
        dcc.Graph(id='temporal_trends')
    ],
    fluid=True
)

# Define the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.layout = layout


# Callback to populate year dropdowns
@app.callback(
    [Output('specific-year-dropdown', 'options'), Output('specific-years-dropdown', 'options')],
    [Input('url', 'pathname')]
)
def populate_year_dropdowns(pathname):
    if pathname == '/sub_page3b':
        query = "SELECT DISTINCT Year FROM fire_data"
        df_years = load_data_from_sqlite(query)
        year_options = [{'label': str(year), 'value': year} for year in df_years['Year'].unique()]
        return year_options, year_options
    return [], []


# Callback to update the specific analysis graph
@app.callback(
    Output('specific_analysis', 'figure'),
    [Input('analyze-button', 'n_clicks')],
    [State('specific-year-dropdown', 'value'), State('specific-month-dropdown', 'value')]
)
def update_specific_analysis(n_clicks, year, month):
    if n_clicks and year and month:
        query = f"SELECT * FROM fire_data WHERE Year={year} AND strftime('%m', ACQ_DATE)='{month:02}'"
        df_filtered = load_data_from_sqlite(query)
        specific_counts = df_filtered['ACQ_DATE'].value_counts().sort_index().reset_index()
        specific_counts.columns = ['ACQ_DATE', 'counts']
        specific_fig = px.line(specific_counts, x='ACQ_DATE', y='counts', markers=True,
                               title=f'Fire Occurrences for {year}-{month:02}')
        specific_fig.update_layout(xaxis_title='Date', yaxis_title='Number of Fires')
        log_memory_usage()  # Log memory usage
        gc.collect()  # Explicitly run garbage collection to free up memory
        return specific_fig
    return {}


# Callback to update the temporal trends graph
@app.callback(
    Output('temporal_trends', 'figure'),
    [Input('specific-years-dropdown', 'value')]
)
def update_temporal_trends(years):
    if years:
        query = f"SELECT * FROM fire_data WHERE Year IN ({','.join(map(str, years))})"
        df_filtered = load_data_from_sqlite(query)
        df_filtered['ACQ_DATE'] = pd.to_datetime(df_filtered['ACQ_DATE'])
        monthly_counts = df_filtered.groupby(['Year', df_filtered['ACQ_DATE'].dt.month]).size().unstack(level=0).fillna(
            0)
        temporal_fig = go.Figure()
        for yr in years:
            temporal_fig.add_trace(
                go.Scatter(x=monthly_counts.index, y=monthly_counts[yr], mode='lines+markers', name=str(yr)))
        temporal_fig.update_layout(title='Monthly Fire Occurrences for Specific Years', xaxis_title='Month',
                                   yaxis_title='Number of Fires')
        temporal_fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)),
                                  ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov',
                                            'Dec'])
        log_memory_usage()  # Log memory usage
        gc.collect()  # Explicitly run garbage collection to free up memory
        return temporal_fig
    return {}


# Register the callbacks
def register_callbacks(app):
    app.callback(
        Output('specific_analysis', 'figure'),
        [Input('analyze-button', 'n_clicks')],
        [State('specific-year-dropdown', 'value'), State('specific-month-dropdown', 'value')]
    )(update_specific_analysis)

    app.callback(
        Output('temporal_trends', 'figure'),
        [Input('specific-years-dropdown', 'value')]
    )(update_temporal_trends)

    app.callback(
        [Output('specific-year-dropdown', 'options'), Output('specific-years-dropdown', 'options')],
        [Input('url', 'pathname')]
    )(populate_year_dropdowns)


register_callbacks(app)

