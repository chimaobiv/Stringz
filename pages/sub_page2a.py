import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
from PIL import Image
import torch
from sam2.sam2_image_predictor import SAM2ImagePredictor
from sam2.sam2_video_predictor import SAM2VideoPredictor
import base64
import io
import cv2
import tempfile
import os

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
                html.H3("Upload an Image or Video"),
                dcc.Upload(
                    id='upload-media',
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
                dcc.Input(id='input-prompt', type='text', placeholder='Enter detection prompt...',
                          style={'width': '100%'}),
                html.Button('Detect', id='detect-button', n_clicks=0, className="mt-2"),
            ], width=4),
            dbc.Col([
                html.H3("Uploaded Media"),
                html.Div(id='media-preview-container'),
                html.Hr(),
                html.H3("Detected Output"),
                html.Div(id='detected-output-container')
            ], width=8)
        ])
    ],
    fluid=True
)


# Function to parse uploaded media
def parse_media(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return decoded, filename


# Function to perform image detection using Hugging Face model
def perform_image_detection(image_data, prompt):
    predictor = SAM2ImagePredictor.from_pretrained("facebook/sam2-hiera-large")

    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
        image = Image.open(io.BytesIO(image_data))
        predictor.set_image(image)
        masks, _, _ = predictor.predict(prompt)

    return masks


# Function to perform video detection using Hugging Face model
def perform_video_detection(video_data, prompt):
    predictor = SAM2VideoPredictor.from_pretrained("facebook/sam2-hiera-large")

    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            temp_video.write(video_data)
            temp_video_path = temp_video.name

        cap = cv2.VideoCapture(temp_video_path)
        frames = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        state = predictor.init_state(frames)
        frame_idx, object_ids, masks = predictor.add_new_points_or_box(state, prompt)

        os.remove(temp_video_path)  # Clean up temporary file

    return masks


def register_callbacks(app):
    @app.callback(
        [
            Output('media-preview-container', 'children'),
            Output('detected-output-container', 'children')
        ],
        [Input('upload-media', 'contents')],
        [State('upload-media', 'filename')]
    )
    def display_uploaded_media(media_contents, media_filename):
        if media_contents:
            media_data, filename = parse_media(media_contents, media_filename)

            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                original_img = Image.open(io.BytesIO(media_data))
                original_img_fig = px.imshow(original_img)
                return dcc.Graph(figure=original_img_fig), None

            elif filename.lower().endswith(('.mp4', '.mov')):
                video_preview = html.Video(src=media_contents, controls=True, style={'width': '100%'})
                return video_preview, None

        return None, None

    @app.callback(
        [
            Output('detected-output-container', 'children')
        ],
        [Input('detect-button', 'n_clicks')],
        [State('upload-media', 'contents'), State('upload-media', 'filename'), State('input-prompt', 'value')]
    )
    def detect_media(n_clicks, media_contents, media_filename, prompt):
        if n_clicks > 0 and media_contents:
            media_data, filename = parse_media(media_contents, media_filename)

            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                detected_img = perform_image_detection(media_data, prompt)
                detected_img_fig = px.imshow(detected_img)
                return [dcc.Graph(figure=detected_img_fig)]

            elif filename.lower().endswith(('.mp4', '.mov')):
                detected_video = perform_video_detection(media_data, prompt)
                # Placeholder for detected video
                return [html.Div("Video detection completed. Results processed.")]

        return [None]


register_callbacks(app)
