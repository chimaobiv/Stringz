import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import geopandas as gpd
import dask.dataframe as dd
from shapely import wkb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import json
# Load secrets
with open('config/secrets.json') as f:
    secrets = json.load(f)
    api_key = secrets['tomtom_api_key']
    mapbox_access_token = secrets['mapbox_access_token']

# Load the parquet file in chunks
def load_geojson_chunk(parquet_file_path, npartitions=2):
    start_time = time.time()

    # Read Parquet file using Dask
    ddf = dd.read_parquet(parquet_file_path)

    # Convert to GeoPandas DataFrame
    df = ddf.compute()

    # Convert the geometry column from WKB to shapely geometries
    df['geometry'] = df['geometry'].apply(wkb.loads)

    # Ensure geometry column is recognized as geometry
    gdf = gpd.GeoDataFrame(df, geometry='geometry')

    end_time = time.time()
    print(f"Time taken to load Parquet file: {end_time - start_time} seconds")

    return dd.from_pandas(gdf, npartitions=npartitions)

# Load the parquet data
parquet_file_path = '/Users/cobi/PycharmProjects/project_ai/data/fire_archive_M-C61_490372.parquet'
gdf_chunked = load_geojson_chunk(parquet_file_path)
df = gdf_chunked.compute()

# Convert the ACQ_DATE to datetime format
try:
    df['ACQ_DATE'] = pd.to_datetime(df['ACQ_DATE'])
except Exception as e:
    print(f"Error converting ACQ_DATE to datetime: {e}")

df['Year'] = df['ACQ_DATE'].dt.year

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
            options=[{'label': str(year), 'value': year} for year in df['Year'].unique()],
            placeholder="Select Year"
        ),
        dcc.Dropdown(
            id='specific-month-dropdown',
            options=[{'label': 'January', 'value': 1}, {'label': 'February', 'value': 2},
                     {'label': 'March', 'value': 3},
                     {'label': 'April', 'value': 4}, {'label': 'May', 'value': 5}, {'label': 'June', 'value': 6},
                     {'label': 'July', 'value': 7}, {'label': 'August', 'value': 8},
                     {'label': 'September', 'value': 9},
                     {'label': 'October', 'value': 10}, {'label': 'November', 'value': 11},
                     {'label': 'December', 'value': 12}],
            placeholder="Select Month"
        ),
        dbc.Button("Analyze", id="analyze-button", color="primary", className="mt-2"),
        dcc.Graph(id='specific_analysis'),
        html.H3("Temporal Trends for Specific Years"),
        dcc.Dropdown(
            id='specific-years-dropdown',
            options=[{'label': str(year), 'value': year} for year in df['Year'].unique()],
            multi=True,
            placeholder="Select Years"
        ),
        dcc.Graph(id='temporal_trends')
    ],
    fluid=True
)

def register_callbacks(app):
    @app.callback(
        Output('specific_analysis', 'figure'),
        [Input('analyze-button', 'n_clicks')],
        [State('specific-year-dropdown', 'value'), State('specific-month-dropdown', 'value')]
    )
    def update_specific_analysis(n_clicks, year, month):
        if n_clicks and year and month:
            df_filtered = df[(df['Year'] == year) & (df['ACQ_DATE'].dt.month == month)]
            specific_counts = df_filtered['ACQ_DATE'].value_counts().sort_index().reset_index()
            specific_counts.columns = ['ACQ_DATE', 'counts']
            specific_fig = px.line(specific_counts, x='ACQ_DATE', y='counts', markers=True,
                                   title=f'Fire Occurrences for {year}-{month:02}')
            specific_fig.update_layout(xaxis_title='Date', yaxis_title='Number of Fires')
            return specific_fig
        return {}

    @app.callback(
        Output('temporal_trends', 'figure'),
        [Input('specific-years-dropdown', 'value')]
    )
    def update_temporal_trends(years):
        if years:
            df_filtered = df[df['Year'].isin(years)]
            monthly_counts = df_filtered.groupby(['Year', df_filtered['ACQ_DATE'].dt.month]).size().unstack(level=0).fillna(0)
            temporal_fig = go.Figure()
            for yr in years:
                temporal_fig.add_trace(go.Scatter(x=monthly_counts.index, y=monthly_counts[yr], mode='lines+markers', name=str(yr)))
            temporal_fig.update_layout(title='Monthly Fire Occurrences for Specific Years', xaxis_title='Month', yaxis_title='Number of Fires')
            temporal_fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)),
                                      ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            return temporal_fig
        return {}

# Define the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.layout = layout
register_callbacks(app)
