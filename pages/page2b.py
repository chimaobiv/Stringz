import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import googlemaps
from datetime import datetime
import json

# Load the Google Maps API key from the secrets.json file
with open('config/secrets.json') as f:
    secrets = json.load(f)
    gmaps_api_key = secrets['googlemaps_api_key']
    mapbox_access_token = secrets['mapbox_access_token']

# Initialize the Google Maps client with the API key
gmaps = googlemaps.Client(key=gmaps_api_key)

# Options for places
place_type_options = [
    {"label": "Hospital", "value": "hospital"},
    {"label": "Mall", "value": "shopping_mall"},
    {"label": "Church", "value": "church"},
    {"label": "Gas Station", "value": "gas_station"},
    {"label": "Police Station", "value": "police"},
    {"label": "Park", "value": "park"}
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
                        dbc.NavItem(dbc.Input(id="current-address-input", placeholder="Enter current address...", type="text", className="mb-2")),
                        dbc.NavItem(dbc.Select(id="place-type-dropdown", options=place_type_options, placeholder="Select Place Type", className="mb-2")),
                        dbc.NavItem(dbc.Button("Find Nearest Place", id="find-place-button", color="primary", className="mb-2")),
                    ],
                    vertical=True,
                    pills=True,
                ),
                width=3
            ),
            dbc.Col(
                html.Div(id="main-content", children=[
                    dcc.Graph(id='mapbox-graph', config={'displayModeBar': False}, style={"height": "600px"})  # Placeholder for the map
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
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    print(f"Geocode request failed for address: {address}")
    return None, None

def find_nearest_place(current_coords, place_type):
    places_result = gmaps.places_nearby(location=current_coords, radius=5000, type=place_type)
    if places_result['results']:
        place = places_result['results'][0]
        location = place['geometry']['location']
        place_name = place['name']
        place_address = place['vicinity']
        return location['lat'], location['lng'], place_name, place_address
    print(f"No places found for type: {place_type}")
    return None, None, None, None

def get_directions(origin_coords, destination_coords):
    directions_result = gmaps.directions(origin=origin_coords,
                                         destination=destination_coords,
                                         mode='driving',
                                         alternatives=True,
                                         departure_time=datetime.now(),
                                         traffic_model='best_guess')
    if directions_result:
        recommended_route = directions_result[0]['legs'][0]['steps']
        route_coordinates = [(step['start_location']['lat'], step['start_location']['lng']) for step in recommended_route]
        route_coordinates.append((recommended_route[-1]['end_location']['lat'], recommended_route[-1]['end_location']['lng']))
        distance = directions_result[0]['legs'][0]['distance']['text']
        return route_coordinates, distance
    print(f"Directions request failed from {origin_coords} to {destination_coords}")
    return [], None

def snap_to_roads(route_coordinates):
    path = '|'.join([f"{lat},{lng}" for lat, lng in route_coordinates])
    snapped_points_result = gmaps.snap_to_roads(path=path, interpolate=True)
    snapped_route_coordinates = [(point['location']['latitude'], point['location']['longitude']) for point in snapped_points_result]
    return snapped_route_coordinates

def update_map(n_clicks, current_address, place_type):
    if n_clicks and current_address and place_type:
        start_lat, start_lon = geocode_address(current_address)
        if start_lat and start_lon:
            start_coords = (start_lat, start_lon)
            end_lat, end_lon, place_name, place_address = find_nearest_place(start_coords, place_type)
            if end_lat and end_lon:
                end_coords = (end_lat, end_lon)
                route_coordinates, distance = get_directions(start_coords, end_coords)
                if route_coordinates:
                    snapped_route_coords = snap_to_roads(route_coordinates)
                    route_df = pd.DataFrame(snapped_route_coords, columns=['Latitude', 'Longitude'])
                    points_df = pd.DataFrame([
                        {'Latitude': start_coords[0], 'Longitude': start_coords[1], 'Type': 'Current Location'},
                        {'Latitude': end_coords[0], 'Longitude': end_coords[1], 'Type': f'Nearest {place_type.capitalize()}'}
                    ])

                    fig = px.scatter_mapbox(points_df, lat='Latitude', lon='Longitude', color='Type',
                                            size=[20, 20], size_max=15, zoom=13, height=600)

                    fig.add_trace(px.line_mapbox(route_df, lat='Latitude', lon='Longitude').data[0])

                    fig.update_layout(mapbox_style="streets", mapbox_accesstoken=mapbox_access_token)
                    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

                    return fig, f"Route to nearest {place_type.capitalize()} found. Distance: {distance}. Address: {place_address}. Name: {place_name}."
                else:
                    return create_empty_map(), "Route calculation failed. Please try again."
            else:
                return create_empty_map(), f"No {place_type.capitalize()} found near the location."
        else:
            return create_empty_map(), "Geocoding failed. Please check the address."
    return create_empty_map(), "Please enter a valid address and select a place type."

def create_empty_map():
    empty_df = pd.DataFrame(columns=['Latitude', 'Longitude'])
    fig = px.scatter_mapbox(
        empty_df,
        lat='Latitude',
        lon='Longitude',
        zoom=1,
        mapbox_style="streets"
    )
    fig.update_layout(mapbox_accesstoken=mapbox_access_token)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

# Register the callback
def register_callbacks(app):
    app.callback(
        [Output('mapbox-graph', 'figure', allow_duplicate=True), Output('route-info', 'children', allow_duplicate=True)],
        [Input('find-place-button', 'n_clicks')],
        [
            State('current-address-input', 'value'),
            State('place-type-dropdown', 'value')
        ],
        prevent_initial_call=True
    )(update_map)
