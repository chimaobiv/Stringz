import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
from PIL import Image, ImageOps, UnidentifiedImageError
import torch
from sam2.sam2_image_predictor import SAM2ImagePredictor
from sam2.sam2_video_predictor import SAM2VideoPredictor
import base64
import io
import json
import os
import tempfile
import subprocess
import numpy as np

# Set the maximum allowed file size (20 MB in bytes)
MAX_FILE_SIZE = 20 * 1024 * 1024

# Ensure fallback to CPU for unsupported MPS operations
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

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
                html.Button('Predict', id='predict-button', n_clicks=0, className="mt-2"),
                html.Div(id='error-message', style={'color': 'red', 'margin-top': '10px'})  # Error message display
            ], width=4),
            dbc.Col([
                html.H3("Uploaded Media"),
                html.Div(id='media-preview-container'),
                html.Hr(),
                html.H3("Detected Output"),
                html.Div(id='detected-output-container')
            ], width=8)
        ]),
        dcc.Markdown("Selected Region Coordinates:"),
        html.Pre(id="annotations-pre"),
    ],
    fluid=True
)

# Define the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.layout = layout

# Setup device for computation
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"Using device: {device}")

# Load the SAM2 models from Hugging Face
image_predictor = SAM2ImagePredictor.from_pretrained("facebook/sam2-hiera-large", device=device)
video_predictor = SAM2VideoPredictor.from_pretrained("facebook/sam2-hiera-large", device=device)

# Function to parse uploaded media
def parse_media(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return decoded, filename

# Function to perform image detection
def perform_image_detection(image_data, point_coords, point_labels):
    try:
        image = Image.open(io.BytesIO(image_data))
    except UnidentifiedImageError:
        return None, None, None

    image_predictor.set_image(image)

    masks, scores, logits = image_predictor.predict(
        point_coords=point_coords,
        point_labels=point_labels,
        multimask_output=True
    )

    return masks, scores, np.array(image)

# Function to extract frames from video
def extract_frames(video_data, output_dir):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        temp_video.write(video_data)
        temp_video_path = temp_video.name

    os.makedirs(output_dir, exist_ok=True)
    output_pattern = f"{output_dir}/%05d.jpg"
    command = f"ffmpeg -i {temp_video_path} -q:v 2 -start_number 0 {output_pattern}"

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg error: {e}")
    finally:
        os.remove(temp_video_path)

    return output_dir

# Function to overlay mask on image
def overlay_mask(image, mask):
    mask = mask.astype(np.uint8)
    mask_color = np.array([30, 144, 255, 128], dtype=np.uint8)  # RGBA for mask overlay
    mask = Image.fromarray(mask * 255).convert("L")
    mask_color = ImageOps.colorize(mask, black="black", white="blue").convert("RGBA")
    mask_color.putalpha(128)

    # Ensure mask and image dimensions match
    if image.size != mask_color.size:
        mask_color = mask_color.resize(image.size, Image.ANTIALIAS)

    combined = Image.alpha_composite(image.convert("RGBA"), mask_color)
    return combined

def register_callbacks(app):
    @app.callback(
        [
            Output('media-preview-container', 'children'),
            Output('error-message', 'children')
        ],
        [Input('upload-media', 'contents')],
        [State('upload-media', 'filename')]
    )
    def display_uploaded_media(media_contents, media_filename):
        if media_contents:
            media_data, filename = parse_media(media_contents, media_filename)

            if len(media_data) > MAX_FILE_SIZE:
                return None, "File size exceeds the 20 MB limit. Please upload a smaller file."

            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                original_img = Image.open(io.BytesIO(media_data))
                fig = px.imshow(original_img)
                fig.update_layout(dragmode="drawrect")
                config = {
                    "modeBarButtonsToAdd": [
                        "drawline",
                        "drawopenpath",
                        "drawclosedpath",
                        "drawcircle",
                        "drawrect",
                        "eraseshape",
                    ]
                }
                return dcc.Graph(id="fig-image", figure=fig, config=config), ""

            elif filename.lower().endswith(('.mp4', '.mov')):
                output_dir = tempfile.mkdtemp()
                extract_frames(media_data, output_dir)
                frame_path = os.path.join(output_dir, "00000.jpg")
                fig = px.imshow(Image.open(frame_path))
                fig.update_layout(dragmode="drawrect")
                config = {
                    "modeBarButtonsToAdd": [
                        "drawline",
                        "drawopenpath",
                        "drawclosedpath",
                        "drawcircle",
                        "drawrect",
                        "eraseshape",
                    ]
                }
                return dcc.Graph(id="fig-image", figure=fig, config=config), ""

        return None, ""

    @app.callback(
        Output('annotations-pre', 'children'),
        Input('fig-image', 'relayoutData'),
        prevent_initial_call=True,
    )
    def on_new_annotation(relayout_data):
        if relayout_data is not None:
            if "shapes" in relayout_data:
                shapes = relayout_data["shapes"]
                coords = {
                    'x0': shapes[0]['x0'],
                    'y0': shapes[0]['y0'],
                    'x1': shapes[0]['x1'],
                    'y1': shapes[0]['y1'],
                }
                print(f"Selected region coordinates: {coords}")  # Debugging
                return json.dumps(coords, indent=2)
        return "No annotation data available."

    @app.callback(
        Output('detected-output-container', 'children'),
        Input('predict-button', 'n_clicks'),
        State('annotations-pre', 'children'),
        State('upload-media', 'contents'),
        State('upload-media', 'filename'),
        prevent_initial_call=True
    )
    def detect_from_region(n_clicks, annotation_data, media_contents, media_filename):
        if not annotation_data:
            return "No annotation data available."

        try:
            coords = json.loads(annotation_data)
        except json.JSONDecodeError:
            return "Invalid annotation data format."

        if not coords or not all(k in coords for k in ['x0', 'y0', 'x1', 'y1']):
            return "Invalid region data."

        # Convert to the format required by the predictor
        point_coords = np.array([[coords['x0'], coords['y0']], [coords['x1'], coords['y1']]])
        point_labels = np.array([1, 1])  # Assume both points are positive examples

        media_data, _ = parse_media(media_contents, media_filename)

        if media_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            masks, scores, image = perform_image_detection(media_data, point_coords, point_labels)
        else:
            # Handle video
            output_dir = tempfile.mkdtemp()
            frame_dir = extract_frames(media_data, output_dir)
            inference_state = video_predictor.init_state(video_path=frame_dir)
            masks = []
            for i, frame_name in enumerate(sorted(os.listdir(frame_dir))):
                frame_path = os.path.join(frame_dir, frame_name)
                frame = np.array(Image.open(frame_path))
                _, out_obj_ids, out_mask_logits = video_predictor.add_new_points_or_box(
                    inference_state=inference_state,
                    frame_idx=i,
                    obj_id=1,  # Assumed object ID for now
                    points=point_coords,
                    labels=point_labels
                )
                masks.append((out_mask_logits[0] > 0.0).cpu().numpy())

        if masks is not None and len(masks) > 0:
            if media_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                detected_image = overlay_mask(Image.fromarray(image), masks[0])
                detected_image = detected_image.convert("RGB")  # Convert back to RGB
                fig = px.imshow(np.array(detected_image))
                return dcc.Graph(figure=fig)
            else:
                mask_to_display = masks[0]
                if mask_to_display.ndim == 3 and mask_to_display.shape[0] == 1:
                    mask_to_display = mask_to_display.squeeze(0)  # Remove the extra dimension
                fig = px.imshow(mask_to_display)
                return dcc.Graph(figure=fig)
        else:
            return "No valid masks found."

register_callbacks(app)

