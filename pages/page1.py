import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import urllib.parse as urlparse
import json

# Load the TomTom API key from the secrets.json file
with open('config/secrets.json') as f:
    secrets = json.load(f)
    api_key = secrets['tomtom_api_key']
    mapbox_access_token = secrets['mapbox_access_token']

# Options for dropdowns
route_type_options = [
    {"label": "Fastest", "value": "fastest"},
    {"label": "Shortest", "value": "short"}
]

traffic_options = [
    {"label": "Live", "value": "live"},
    {"label": "Historical", "value": "historical"}
]

travel_mode_options = [
    {"label": "Car", "value": "car"},
    {"label": "Truck", "value": "truck"}
]

avoid_options = [
    {"label": "Unpaved Roads", "value": "unpavedRoads"},
    {"label": "Toll Roads", "value": "tollRoads"},
    {"label": "Motorways", "value": "motorways"},
    {"label": "Ferries", "value": "ferries"}
]

layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(
                dbc.Button("Back to Main Page", href="/", color="primary", className="mb-4"),
                width=12
            )
        ]),
        dbc.Row([
            dbc.Col(
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.Input(id="start-input", placeholder="Enter start address...", type="text",
                                              className="mb-2")),
                        dbc.NavItem(dbc.Input(id="end-input", placeholder="Enter end address...", type="text",
                                              className="mb-2")),
                        dbc.NavItem(dbc.Select(id="route-type-dropdown", options=route_type_options,
                                               placeholder="Select Route Type", className="mb-2")),
                        dbc.NavItem(
                            dbc.Select(id="traffic-dropdown", options=traffic_options, placeholder="Select Traffic",
                                       className="mb-2")),
                        dbc.NavItem(dbc.Select(id="travel-mode-dropdown", options=travel_mode_options,
                                               placeholder="Select Travel Mode", className="mb-2")),
                        dbc.NavItem(
                            dbc.Select(id="avoid-dropdown", options=avoid_options, placeholder="Select Avoid Option",
                                       className="mb-2")),
                        dbc.NavItem(dcc.DatePickerSingle(
                            id='depart-at-input',
                            placeholder='Select departure date',
                            className="mb-2"
                        )),
                        dbc.NavItem(dbc.Checklist(
                            options=[
                                {"label": "Commercial Vehicle", "value": "true"}
                            ],
                            value=[],
                            id="vehicle-commercial-checklist",
                            switch=True,
                            className="mb-2"
                        )),
                        dbc.NavItem(
                            dbc.Button("Calculate Route", id="calculate-button", color="primary", className="mb-2")),
                    ],
                    vertical=True,
                    pills=True,
                ),
                width=3
            ),
            dbc.Col(
                html.Div(id="main-content", children=[
                    dcc.Graph(id='mapbox-graph', config={'displayModeBar': False}, style={"height": "600px"})
                    # Placeholder for the map
                ]),
                width=9
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.Div(id="route-info", style={"marginTop": "20px"})
            )
        ])
    ],
    fluid=True
)


def geocode_address(address):
    if not address:
        return None, None
    geocode_base_url = "https://api.tomtom.com/search/2/geocode/"
    geocode_request_url = f"{geocode_base_url}{urlparse.quote(address)}.json?key={api_key}"
    geocode_response = requests.get(geocode_request_url)
    if geocode_response.status_code == 200:
        geocode_data = geocode_response.json()
        if geocode_data['results']:
            position = geocode_data['results'][0]['position']
            return position['lat'], position['lon']
    print(f"Geocode request failed: {geocode_response.status_code}, {geocode_response.text}")
    return None, None


def calculate_routes(start_coords, end_coords, route_type, traffic, travel_mode, avoid, depart_at, vehicle_commercial):
    # Ensure the date is in the correct format
    depart_at = depart_at + "T00:00:00" if "T" not in depart_at else depart_at

    # Ensure vehicle_commercial is a string
    vehicle_commercial = "true" if vehicle_commercial else "false"

    baseUrl = "https://api.tomtom.com/routing/1/calculateRoute/"
    requestParams = (
            urlparse.quote(start_coords) + ":" + urlparse.quote(end_coords)
            + f"/json?routeType={route_type}"
            + f"&traffic={traffic}"
            + f"&travelMode={travel_mode}"
            + f"&avoid={avoid}"
            + f"&vehicleCommercial={vehicle_commercial}"
            + f"&departAt={urlparse.quote(depart_at)}"
            + f"&maxAlternatives=2"
    )

    requestUrl = baseUrl + requestParams + "&key=" + api_key

    response = requests.get(requestUrl)

    if response.status_code == 200:
        jsonResult = response.json()
        routes = []
        for route in jsonResult['routes']:
            routeSummary = route['summary']
            eta = routeSummary['arrivalTime']
            travelTime = routeSummary['travelTimeInSeconds'] / 3600
            legs = route['legs'][0]['points']
            route_coords = [(point['latitude'], point['longitude']) for point in legs]
            routes.append((eta, travelTime, route_coords))
        return routes
    else:
        return []


def get_traffic_data(point):
    base_url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    request_url = f"{base_url}?key={api_key}&point={point}"
    try:
        response = requests.get(request_url)
        if response.status_code == 200:
            traffic_data = response.json()
            return traffic_data["flowSegmentData"]
        elif response.status_code == 403:
            print(f"Traffic data request limit exceeded.")
        else:
            print(f"Traffic data request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"An error occurred during traffic data fetching: {e}")
    return None


def get_traffic_color(current_speed, free_flow_speed):
    if current_speed >= free_flow_speed * 0.9:
        return "green"
    elif current_speed >= free_flow_speed * 0.6:
        return "yellow"
    else:
        return "red"


def update_map(n_clicks, start_address, end_address, route_type, traffic, travel_mode, avoid, depart_at,
               vehicle_commercial):
    if n_clicks and start_address and end_address:
        start_lat, start_lon = geocode_address(start_address)
        end_lat, end_lon = geocode_address(end_address)
        if start_lat and start_lon and end_lat and end_lon:
            start_coords = f"{start_lat},{start_lon}"
            end_coords = f"{end_lat},{end_lon}"
            routes = calculate_routes(start_coords, end_coords, route_type, traffic, travel_mode, avoid, depart_at,
                                      vehicle_commercial)
            if routes:
                fig = go.Figure()
                route_infos = []

                for route_index, (eta, travelTime, route_coords) in enumerate(routes):
                    route_df = pd.DataFrame(route_coords, columns=['lat', 'lon'])
                    colors = []
                    traffic_data_limit_exceeded = False

                    # Fetch traffic data for each segment and set the color based on the traffic
                    for idx, point in enumerate(route_coords[:-1]):
                        next_point = route_coords[idx + 1]
                        mid_point = ((point[0] + next_point[0]) / 2, (point[1] + next_point[1]) / 2)
                        traffic_data = get_traffic_data(f"{mid_point[0]},{mid_point[1]}")
                        if traffic_data:
                            current_speed = traffic_data["currentSpeed"]
                            free_flow_speed = traffic_data["freeFlowSpeed"]
                            color = get_traffic_color(current_speed, free_flow_speed)
                        else:
                            if traffic_data_limit_exceeded:
                                color = "gray"
                            else:
                                color = "gray"
                                traffic_data_limit_exceeded = True
                        colors.append(color)

                    for i, point in enumerate(route_coords[:-1]):
                        next_point = route_coords[i + 1]
                        fig.add_trace(go.Scattermapbox(
                            lat=[point[0], next_point[0]],
                            lon=[point[1], next_point[1]],
                            mode='lines',
                            line=dict(color=colors[i], width=5),
                            name=f'Route {route_index + 1}'
                        ))

                    fig.add_trace(go.Scattermapbox(
                        lat=[route_df['lat'].iloc[0], route_df['lat'].iloc[-1]],
                        lon=[route_df['lon'].iloc[0], route_df['lon'].iloc[-1]],
                        mode='markers+text',
                        marker=dict(size=12, color=['blue', 'red']),
                        text=["Start", "End"],
                        textposition="top right"
                    ))

                    route_infos.append(f"Route {route_index + 1}: ETA: {eta}, Travel time: {travelTime:.2f} hours")

                fig.update_layout(
                    mapbox=dict(
                        style="carto-positron",
                        accesstoken=mapbox_access_token,
                        zoom=6,
                        center=dict(lat=(start_lat + end_lat) / 2, lon=(start_lon + end_lon) / 2)
                    ),
                    margin={"r": 0, "t": 0, "l": 0, "b": 0}
                )

                return fig, html.Ul([html.Li(info) for info in route_infos])
            else:
                return create_empty_map(), "Route calculation failed. Please try again."
        else:
            return create_empty_map(), "Geocoding failed. Please check the addresses."
    return create_empty_map(), "Please enter both start and end addresses."


def create_empty_map():
    empty_df = pd.DataFrame(columns=['lat', 'lon'])
    fig = px.scatter_mapbox(
        empty_df,
        lat='lat',
        lon='lon',
        zoom=1,
        mapbox_style="carto-positron"
    )
    fig.update_layout(mapbox_accesstoken=mapbox_access_token)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


# Register the callback
def register_callbacks(app):
    app.callback(
        [Output('mapbox-graph', 'figure'), Output('route-info', 'children')],
        [Input('calculate-button', 'n_clicks')],
        [
            State('start-input', 'value'),
            State('end-input', 'value'),
            State('route-type-dropdown', 'value'),
            State('traffic-dropdown', 'value'),
            State('travel-mode-dropdown', 'value'),
            State('avoid-dropdown', 'value'),
            State('depart-at-input', 'date'),
            State('vehicle-commercial-checklist', 'value')
        ]
    )(update_map)
