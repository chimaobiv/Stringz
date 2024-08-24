import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Define the layout for page2.py
layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dbc.Button("Back to Main Page", href="/", color="primary", className="mb-4"),
                width=12
            ),
        ),
        dbc.Row(
            dbc.Col(
                html.H1("Image Detection Project", className="text-center my-4"),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.P(
                    "This project allows users to upload an image and use a machine learning model to detect objects "
                    "within the image. The user can input a prompt to specify what to detect, and the application will "
                    "display the original image alongside the detected image.",
                    className="lead"
                ),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.H3("How it Works"),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Ul([
                    html.Li("Upload an image (JPG or PNG)."),
                    html.Li("Enter a prompt to specify the objects to detect."),
                    html.Li("Click the 'Detect' button to run the model."),
                    html.Li("The original and detected images will be displayed side by side."),
                ]),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.P(
                    "For technical details, we are using a large model hosted on a separate platform to perform the "
                    "detection, while the web interface is hosted on Heroku.",
                    className="lead"
                ),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button("Go to Image Detection", href="/sub_page2a", color="primary", className="mt-4"),
                width=12
            )
        )
    ],
    fluid=True
)
