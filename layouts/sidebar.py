import dash
import dash_bootstrap_components as dbc
from dash import dcc, html


def getSideBarComponent():
    # Sidebar layout
    sidebar = html.Div(
        [
            html.H2("Navigation", className="display-4"),
            html.Hr(),
            html.P("Select an analysis type:", className="lead"),
            dbc.Nav(
                [
                    dbc.NavLink("Solar", href="/solar", active="exact"),
                    dbc.NavLink("Wind", href="/wind", active="exact"),
                    dbc.NavLink("UV", href="/uv", active="exact"),
                    dbc.NavLink("Precipitation", href="/prep", active="exact"),
                    dbc.NavLink("Weather", href="/wth", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style={"width": "20%", "float": "left", "height": "100vh", "padding": "20px"}
    )

    return sidebar

