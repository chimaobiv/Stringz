from dash import dcc, html

def centerComponent(years, initial_data_types):
    dropdown_container = html.Div([
        html.Label("Select Year:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='shared-year-dropdown',
            options=[{'label': str(year), 'value': year} for year in years],
            value=years[0] if years else None  # Default to the most recent year
        ),
        html.Label("Select Data Type:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='shared-data-type-dropdown',
            options=[{'label': data_type, 'value': data_type} for data_type in initial_data_types],
            value=initial_data_types[0] if initial_data_types else None
        )
    ], style={'margin-bottom': '20px', 'width': '100%', 'display': 'inline-block'})

    return dropdown_container
