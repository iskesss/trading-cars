import base64
import json
import streamlit as st
from PIL import Image


# Load logo data once at the start (outside the function)
@st.cache_data  # Cache the data to avoid reloading on every rerun
def load_logo_data():
    with open("logo_icons.json", "r") as f:
        logo_data = json.load(f)
    return {item["name"]: item["logo"] for item in logo_data}


# Create logo dictionary (cached and shared across all cards)
logo_dict = load_logo_data()


# Function to encode the image as base64 and crop it
def get_cropped_image_base64(
    image_path, x1: int = None, y1: int = None, x2: int = None, y2: int = None
):
    # Open the image and crop it
    image = Image.open(image_path)

    if x1 and x1 and x2 and y2:
        cropped_image = image.crop((x1, y1, x2, y2))
    else:
        cropped_image = image

    # Convert the cropped image to base64
    from io import BytesIO

    buffered = BytesIO()
    cropped_image.save(buffered, format="JPEG")
    encoded_string = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{encoded_string}"


# Define the trading card as an HTML template
def trading_card(image_base64, make, model, year, text_color, link_url):
    # Get logo URL for the current vehicle make
    logo_url = logo_dict.get(make, None)

    # Generate logo HTML if available
    logo_html = ""
    if logo_url:
        logo_html = f"""
        <div class="logo-container">
            <img src="{logo_url}" alt="{make} logo" class="logo-image">
        </div>
        """

    card_html = f"""
    <style>
        .card {{
            width: 300px;
            border: 1px solid #ccc;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px {text_color};
            text-align: center;
            display: inline-block;
            margin: 10px;
            position: relative;
        }}
        .card img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .card-text {{
            padding: 10px;
            color: {text_color};
            font-family: Arial, sans-serif;
        }}
        .card a {{
            text-decoration: none;
            color: inherit;
            display: block;
        }}
        .logo-container {{
            position: absolute;
            top: 10px;
            right: 10px;
            width: 50px; /* Container width */
            height: 50px; /* Container height */
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px; /* Rounded corners */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden; /* Ensures the logo doesn't spill out */
        }}
        .logo-image {{
            max-width: 90%; /* Slightly smaller to ensure no cropping */
            max-height: 90%; /* Slightly smaller to ensure no cropping */
            object-fit: contain; /* Ensures the logo fits nicely */
            width: auto; /* Allows the logo to scale naturally */
            height: auto; /* Allows the logo to scale naturally */
        }}
    </style>
    <div class="card">
        <a href="{link_url}" target="_blank">
            <img src="{image_base64}">
            {logo_html}
            <div class="card-text">
                <h3>{make}</h3>
                <p>{model} ({year})</p>
            </div>
        </a>
    </div>
    """
    return card_html
