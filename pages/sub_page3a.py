import gc
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
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


# Function to create datashader image
def create_datashader_image(df, plot_width=800, plot_height=600):
    import datashader as ds
    import datashader.transfer_functions as tf
    from colorcet import fire
    cvs = ds.Canvas(plot_width=plot_width, plot_height=plot_height)
    agg = cvs.points(df, 'LONGITUDE', 'LATITUDE')
    img = tf.shade(agg, cmap=fire, how='log')
    return img


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
        html.H3("Number of Fire Detections per Year (2014-2024)"),
        dcc.Graph(id='fires_per_year'),
        html.H3("Spatial Distribution of Fires (2014-2024)"),
        dcc.Graph(id='spatial_distribution'),
        html.H3("Hexbin Plot of Fire Occurrences (2014-2024)"),
        dcc.Graph(id='hexbin_plot'),
        html.H3("Fire Occurrences by Month (2014-2024)"),
        dcc.Graph(id='monthly_fires'),
        html.H3("Time Series Analysis of Fire Occurrences (2014-2024)"),
        dcc.Graph(id='time_series'),
        html.H3("Trend Analysis of Fire Occurrences (2014-2024)"),
        dcc.Graph(id='trend_analysis'),
        html.H3("Yearly Fire Occurrences (2014-2024)"),
        dcc.Graph(id='yearly_fires'),
        html.H3("Fire Occurrences by Season (2014-2024)"),
        dcc.Graph(id='seasonal_fires'),
        html.H3("Forecast of Fire Occurrences"),
        dcc.Graph(id='forecast_fires')
    ],
    fluid=True
)

# Define the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.layout = layout


# Callback to update the summary graphs
@app.callback(
    [
        Output('fires_per_year', 'figure'),
        Output('spatial_distribution', 'figure'),
        Output('hexbin_plot', 'figure'),
        Output('monthly_fires', 'figure'),
        Output('time_series', 'figure'),
        Output('trend_analysis', 'figure'),
        Output('yearly_fires', 'figure'),
        Output('seasonal_fires', 'figure'),
        Output('forecast_fires', 'figure')
    ],
    [Input('url', 'pathname')]
)
def update_summary(pathname):
    if pathname == '/sub_page3a':
        query = "SELECT * FROM fire_data"
        df = load_data_from_sqlite(query)

        # Convert the ACQ_DATE to datetime format
        try:
            df['ACQ_DATE'] = pd.to_datetime(df['ACQ_DATE'])
        except Exception as e:
            print(f"Error converting ACQ_DATE to datetime: {e}")

        # Optimize data types
        df['Year'] = df['ACQ_DATE'].dt.year.astype('int16')
        df['BRIGHTNESS'] = df['BRIGHTNESS'].astype('float32')
        df['LATITUDE'] = df['LATITUDE'].astype('float32')
        df['LONGITUDE'] = df['LONGITUDE'].astype('float32')
        df['FRP'] = df['FRP'].astype('float32')

        # Number of Fire Detections per Year (2014-2024)
        fires_per_year = df.groupby('Year').size().reset_index(name='counts')
        fig1 = px.line(fires_per_year, x='Year', y='counts', markers=True,
                       title='Number of Fire Detections per Year (2014-2024)')
        fig1.update_layout(xaxis_title='Year', yaxis_title='Number of Fires')

        # Spatial Distribution of Fires (2014-2024) using Datashader
        img = create_datashader_image(df)
        fig2 = px.imshow(img.to_pil(), title='Spatial Distribution of Fires (2014-2024)')
        fig2.update_layout(width=1200, height=800)

        # Hexbin Plot of Fire Occurrences (2014-2024)
        fig3 = px.density_mapbox(df, lat='LATITUDE', lon='LONGITUDE', z='BRIGHTNESS', radius=10,
                                 mapbox_style="stamen-terrain", title='Hexbin Plot of Fire Occurrences (2014-2024)')
        fig3.update_layout(mapbox=dict(accesstoken=mapbox_access_token, center=dict(lat=37, lon=-95), zoom=3),
                           width=1200, height=800)

        # Fire Occurrences by Month (2014-2024)
        df_reset = df.reset_index()
        df_reset['MONTH'] = df_reset['ACQ_DATE'].dt.month
        monthly_counts = df_reset['MONTH'].value_counts().sort_index().reset_index()
        monthly_counts.columns = ['Month', 'counts']
        fig4 = px.bar(monthly_counts, x='Month', y='counts', title='Fire Occurrences by Month (2014-2024)')
        fig4.update_layout(xaxis_title='Month', yaxis_title='Number of Fires', xaxis=dict(tickmode='array',
                                                                                          tickvals=list(range(1, 13)),
                                                                                          ticktext=['Jan', 'Feb', 'Mar',
                                                                                                    'Apr', 'May', 'Jun',
                                                                                                    'Jul', 'Aug', 'Sep',
                                                                                                    'Oct', 'Nov',
                                                                                                    'Dec']))

        # Time Series Analysis of Fire Occurrences (2014-2024)
        time_series = df_reset['ACQ_DATE'].value_counts().sort_index().reset_index()
        time_series.columns = ['ACQ_DATE', 'counts']
        fig5 = px.line(time_series, x='ACQ_DATE', y='counts', markers=True,
                       title='Time Series Analysis of Fire Occurrences (2014-2024)')
        fig5.update_layout(xaxis_title='Date', yaxis_title='Number of Fires')

        # Trend Analysis of Fire Occurrences (2014-2024)
        df_reset.set_index('ACQ_DATE', inplace=True)
        monthly_counts = df_reset.resample('M').size()
        rolling_avg = monthly_counts.rolling(window=6).mean()
        X = monthly_counts.index.map(datetime.toordinal).values.reshape(-1, 1)
        y = monthly_counts.values
        model = LinearRegression()
        model.fit(X, y)
        trend = model.predict(X)
        fig6 = go.Figure()
        fig6.add_trace(
            go.Scatter(x=monthly_counts.index, y=monthly_counts, mode='lines+markers', name='Monthly Fire Occurrences'))
        fig6.add_trace(go.Scatter(x=monthly_counts.index, y=rolling_avg, mode='lines', name='6-Month Rolling Average',
                                  line=dict(color='orange')))
        fig6.add_trace(go.Scatter(x=monthly_counts.index, y=trend, mode='lines', name='Trend Line (Linear Regression)',
                                  line=dict(color='red')))
        fig6.update_layout(title='Trend Analysis of Fire Occurrences (2014-2024)', xaxis_title='Date',
                           yaxis_title='Number of Fires')
        df_reset.reset_index(inplace=True)

        # Yearly Fire Occurrences (2014-2024)
        yearly_counts = df_reset['Year'].value_counts().sort_index().reset_index()
        yearly_counts.columns = ['Year', 'counts']
        fig7 = px.bar(yearly_counts, x='Year', y='counts', title='Yearly Fire Occurrences (2014-2024)')
        fig7.update_layout(xaxis_title='Year', yaxis_title='Number of Fires')

        # Fire Occurrences by Season (2014-2024)
        def categorize_season(date):
            month = date.month
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'

        df_reset['SEASON'] = df_reset['ACQ_DATE'].apply(categorize_season)
        seasonal_counts = df_reset['SEASON'].value_counts().sort_index().reset_index()
        seasonal_counts.columns = ['Season', 'counts']
        fig8 = px.bar(seasonal_counts, x='Season', y='counts', title='Fire Occurrences by Season (2014-2024)')
        fig8.update_layout(xaxis_title='Season', yaxis_title='Number of Fires')

        # Forecast of Fire Occurrences
        if len(monthly_counts.unique()) > 1:  # Ensure there is variability in the data
            result = adfuller(monthly_counts)
            if result[1] > 0.05:
                monthly_counts_diff = monthly_counts.diff().dropna()
            else:
                monthly_counts_diff = monthly_counts
            model = ARIMA(monthly_counts_diff, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=12)
            forecast_dates = pd.date_range(start=monthly_counts.index[-1], periods=12 + 1, freq='M')[1:]
            fig9 = go.Figure()
            fig9.add_trace(go.Scatter(x=monthly_counts.index, y=monthly_counts, mode='lines', name='Historical Data'))
            fig9.add_trace(go.Scatter(x=forecast_dates, y=forecast.cumsum() + monthly_counts.iloc[-1], mode='lines',
                                      name='Forecast', line=dict(color='red', dash='dash')))
            fig9.update_layout(title='Forecast of Fire Occurrences', xaxis_title='Date', yaxis_title='Number of Fires')
        else:
            fig9 = go.Figure()
            fig9.add_trace(go.Scatter(x=monthly_counts.index, y=monthly_counts, mode='lines', name='Historical Data'))
            fig9.update_layout(title='Forecast of Fire Occurrences', xaxis_title='Date', yaxis_title='Number of Fires')

        log_memory_usage()  # Log memory usage
        gc.collect()  # Explicitly run garbage collection to free up memory
        return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9
    return {}, {}, {}, {}, {}, {}, {}, {}, {}


# Register the callbacks
def register_callbacks(app):
    app.callback(
        [
            Output('fires_per_year', 'figure'),
            Output('spatial_distribution', 'figure'),
            Output('hexbin_plot', 'figure'),
            Output('monthly_fires', 'figure'),
            Output('time_series', 'figure'),
            Output('trend_analysis', 'figure'),
            Output('yearly_fires', 'figure'),
            Output('seasonal_fires', 'figure'),
            Output('forecast_fires', 'figure')
        ],
        [Input('url', 'pathname')]
    )(update_summary)


register_callbacks(app)


