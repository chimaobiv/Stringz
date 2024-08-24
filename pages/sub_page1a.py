import gc
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables directly
api_key = os.getenv('weather_api_key')

# Function to fetch weather data
def get_weather_data(location, start_date, end_date, api_key):
    import urllib.request
    import json
    import urllib.parse

    encoded_location = urllib.parse.quote(location)
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    url = f"{base_url}{encoded_location}/{start_date}/{end_date}?unitGroup=metric&include=days&key={api_key}&contentType=json"

    try:
        result_bytes = urllib.request.urlopen(url)
        json_data = json.load(result_bytes)
        days = json_data['days']
        df = pd.DataFrame(days)
        df['location'] = location  # Add location to the dataframe
        return df
    except urllib.error.HTTPError as e:
        error_info = e.read().decode()
        print('Error code:', e.code, error_info)
    except urllib.error.URLError as e:
        error_info = e.read().decode()
        print('Error code:', e.code, error_info)

# Define the layout
layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(
                dbc.Button("Back to Main Page", href="/page1", color="primary", className="mb-4"),
                width=12
            )
        ]),
        html.H3("Weather Analysis Summary"),
        dbc.Row([
            dbc.Col([
                html.Label("Select Locations:"),
                dcc.Dropdown(id='location-dropdown', options=[
                    {'label': 'Atlanta, GA', 'value': 'Atlanta, GA'},
                    {'label': 'New York, NY', 'value': 'New York, NY'},
                    {'label': 'Los Angeles, CA', 'value': 'Los Angeles, CA'},
                    {'label': 'Chicago, IL', 'value': 'Chicago, IL'},
                    {'label': 'Houston, TX', 'value': 'Houston, TX'},
                    {'label': 'Phoenix, AZ', 'value': 'Phoenix, AZ'},
                    {'label': 'Philadelphia, PA', 'value': 'Philadelphia, PA'},
                    {'label': 'San Antonio, TX', 'value': 'San Antonio, TX'},
                    {'label': 'San Diego, CA', 'value': 'San Diego, CA'},
                    {'label': 'Dallas, TX', 'value': 'Dallas, TX'}
                ], value=['Atlanta, GA'], multi=True, style={'margin-bottom': '20px'})
            ], width=6),
            dbc.Col([
                html.Label("Select Date Range:"),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date='2024-08-01',
                    end_date='2024-08-06',
                    display_format='YYYY-MM-DD',
                    style={'margin-bottom': '20px'}
                )
            ], width=6)
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Select Temperature Type:"),
                dcc.Dropdown(id='temp-type-dropdown', options=[
                    {'label': 'Max Temperature', 'value': 'tempmax'},
                    {'label': 'Min Temperature', 'value': 'tempmin'},
                    {'label': 'Average Temperature', 'value': 'temp'}
                ], value='temp', style={'margin-bottom': '20px'})
            ], width=6),
            dbc.Col([
                html.Label("Select Correlation Type:"),
                dcc.Dropdown(id='correlation-type-dropdown', options=[
                    {'label': 'Humidity', 'value': 'humidity'},
                    {'label': 'Wind Speed', 'value': 'windspeed'},
                    {'label': 'Precipitation', 'value': 'precip'},
                    {'label': 'Solar Radiation', 'value': 'solarradiation'}
                ], value='humidity', style={'margin-bottom': '20px'})
            ], width=6)
        ]),
        dbc.Button("Analyze", id="analyze-button", color="primary", className="mb-4"),
        dcc.Graph(id='temperature-trend-graph'),
        dcc.Graph(id='temp-variation-graph'),
        dcc.Graph(id='correlation-scatter-graph'),
        dcc.Graph(id='seasonal-avg-temp-graph'),
        dcc.Graph(id='seasonal-avg-temp-var-graph'),
        dcc.Graph(id='avg-temp-by-location-graph'),
        dcc.Graph(id='solar-trend-graph'),
        dcc.Graph(id='seasonal-avg-solar-graph')
    ],
    fluid=True
)

# Define the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.layout = layout

def register_callbacks(app):
    @app.callback(
        [
            Output('temperature-trend-graph', 'figure'),
            Output('temp-variation-graph', 'figure'),
            Output('correlation-scatter-graph', 'figure'),
            Output('seasonal-avg-temp-graph', 'figure'),
            Output('seasonal-avg-temp-var-graph', 'figure'),
            Output('avg-temp-by-location-graph', 'figure'),
            Output('solar-trend-graph', 'figure'),
            Output('seasonal-avg-solar-graph', 'figure')
        ],
        Input('analyze-button', 'n_clicks'),
        State('location-dropdown', 'value'),
        State('date-picker-range', 'start_date'),
        State('date-picker-range', 'end_date'),
        State('temp-type-dropdown', 'value'),
        State('correlation-type-dropdown', 'value')
    )
    def update_graphs(n_clicks, locations, start_date, end_date, temp_type, corr_type):
        if n_clicks:
            combined_data = pd.DataFrame()
            for location in locations:
                weather_data = get_weather_data(location, start_date, end_date, api_key)
                combined_data = pd.concat([combined_data, weather_data])

            combined_data['datetime'] = pd.to_datetime(combined_data['datetime'])
            combined_data['temp_variation'] = combined_data['tempmax'] - combined_data['tempmin']

            # Temperature Trend Graph
            temp_trend_fig = px.line(combined_data, x='datetime', y=temp_type, color='location',
                                     labels={'value': 'Temperature (°C)', 'datetime': 'Date'},
                                     title=f'{temp_type.replace("temp", "").capitalize()} Temperature Trends Over Time')

            # Temperature Variation Graph
            temp_var_fig = px.line(combined_data, x='datetime', y='temp_variation', color='location',
                                   labels={'temp_variation': 'Temperature Variation (°C)', 'datetime': 'Date'},
                                   title='Daily Temperature Variation Over Time')

            # Correlation Scatter Graph
            corr_scatter_fig = px.scatter(combined_data, x='temp', y=corr_type, color='location',
                                          labels={'temp': 'Temperature (°C)', corr_type: f'{corr_type.capitalize()} (%)'},
                                          title=f'Scatter Plot of Temperature vs. {corr_type.capitalize()}')

            # Seasonal Average Temperature Graph
            combined_data['season'] = combined_data['datetime'].dt.month % 12 // 3 + 1
            combined_data['season'] = combined_data['season'].map({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'})
            seasonal_avg_temp = combined_data.groupby(['season', 'location'])[temp_type].mean().reset_index()
            seasonal_avg_temp_fig = px.bar(seasonal_avg_temp, x='season', y=temp_type, color='location',
                                           labels={temp_type: 'Temperature (°C)', 'season': 'Season'},
                                           title='Average Temperature by Season')

            # Seasonal Average Temperature Variation Graph
            seasonal_avg_temp_var = combined_data.groupby(['season', 'location'])['temp_variation'].mean().reset_index()
            seasonal_avg_temp_var_fig = px.bar(seasonal_avg_temp_var, x='season', y='temp_variation', color='location',
                                               labels={'temp_variation': 'Temperature Variation (°C)', 'season': 'Season'},
                                               title='Average Temperature Variation by Season')

            # Average Temperature by Location Graph
            avg_temp_by_location = combined_data.groupby('location')[temp_type].mean().reset_index()
            avg_temp_by_location_fig = px.bar(avg_temp_by_location, x='location', y=temp_type,
                                              labels={temp_type: 'Average Temperature (°C)', 'location': 'Location'},
                                              title='Average Temperature by Location')

            # Solar Radiation Trend Graph
            solar_trend_fig = px.line(combined_data, x='datetime', y='solarradiation', color='location',
                                      labels={'solarradiation': 'Solar Radiation (W/m²)', 'datetime': 'Date'},
                                      title='Solar Radiation Trends Over Time')

            # Seasonal Average Solar Radiation Graph
            seasonal_avg_solar = combined_data.groupby(['season', 'location'])['solarradiation'].mean().reset_index()
            seasonal_avg_solar_fig = px.bar(seasonal_avg_solar, x='season', y='solarradiation', color='location',
                                            labels={'solarradiation': 'Solar Radiation (W/m²)', 'season': 'Season'},
                                            title='Average Solar Radiation by Season')

            return temp_trend_fig, temp_var_fig, corr_scatter_fig, seasonal_avg_temp_fig, seasonal_avg_temp_var_fig, avg_temp_by_location_fig, solar_trend_fig, seasonal_avg_solar_fig
        return {}, {}, {}, {}, {}, {}, {}, {}

register_callbacks(app)

