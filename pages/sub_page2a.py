import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
from PIL import Image
import base64
import io

# Define the layout for sub_page2a.py
layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(
                dbc.Button("Back to Main Page", href="/page2", color="primary", className="mb-4"),
                width=12
            )
        ]),
        dbc.Row([
            dbc.Col([
                html.H3("Upload an Image"),
                dcc.Upload(
                    id='upload-image',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select a File')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin-bottom': '20px'
                    }
                ),
                html.H3("Enter Detection Prompt"),
                dcc.Input(id='input-prompt', type='text', placeholder='Enter detection prompt...', style={'width': '100%'}),
                html.Button('Detect', id='detect-button', n_clicks=0, className="mt-2"),
            ], width=4),
            dbc.Col([
                html.H3("Original Image"),
                html.Div(id='original-image-container'),
                html.Hr(),
                html.H3("Detected Image"),
                html.Div(id='detected-image-container')
            ], width=8)
        ])
    ],
    fluid=True
)

# Define the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.layout = layout

# Function to parse uploaded image
def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return Image.open(io.BytesIO(decoded))

# Function to perform image detection (placeholder)
def perform_detection(image, prompt):
    # Placeholder logic, replace with actual detection code
    return image

def register_callbacks(app):
    @app.callback(
        Output('original-image-container', 'children'),
        [Input('upload-image', 'contents')]
    )
    def display_uploaded_image(image_contents):
        if image_contents:
            try:
                original_img = parse_contents(image_contents)
                original_img_fig = px.imshow(original_img)
                original_img_fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                return dcc.Graph(figure=original_img_fig)
            except Exception as e:
                print(f"Error displaying image: {e}")
                return html.Div("There was an error displaying the image.")
        return None

    @app.callback(
        Output('detected-image-container', 'children'),
        [Input('detect-button', 'n_clicks')],
        [State('upload-image', 'contents'), State('input-prompt', 'value')]
    )
    def update_detected_image(n_clicks, image_contents, prompt):
        if n_clicks > 0 and image_contents:
            try:
                original_img = parse_contents(image_contents)
                detected_img = perform_detection(original_img, prompt)

                detected_img_fig = px.imshow(detected_img)
                detected_img_fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))

                return dcc.Graph(figure=detected_img_fig)
            except Exception as e:
                print(f"Error processing image: {e}")
                return html.Div("There was an error processing the image.")
        return None

register_callbacks(app)

