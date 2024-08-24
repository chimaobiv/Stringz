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
                html.H1("Advanced Image and Video Detection Project", className="text-center my-4"),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.P(
                    "This project allows users to upload an image or video and utilize a state-of-the-art machine learning model "
                    "to detect objects within the media. Users can input a prompt to specify the objects or regions of interest, "
                    "and the application will display the original and detected outputs side by side.",
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
                    html.Li("Upload an image (JPG or PNG) or video (MP4 or MOV)."),
                    html.Li("Enter a prompt to specify the objects or regions to detect."),
                    html.Li("Click the 'Detect' button to initiate the detection process."),
                    html.Li("The original and detected media will be displayed side by side, showcasing the model's predictions."),
                    html.Li("This application leverages advanced models hosted on Hugging Face, ensuring efficient processing even for large files."),
                ]),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.P(
                    "The backend of this project is powered by Hugging Face models, which are loaded and executed on the fly. "
                    "This enables the application to handle large models without the need for extensive local resources. "
                    "The web interface itself is hosted on Heroku, providing a seamless user experience.",
                    className="lead"
                ),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button("Go to Image and Video Detection", href="/sub_page2a", color="primary", className="mt-4"),
                width=12
            )
        )
    ],
    fluid=True
)
