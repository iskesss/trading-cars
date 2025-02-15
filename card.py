import base64
import json
import streamlit as st
from PIL import Image
from core import get_car_stats


# Load logo data once at the start (outside the function)
@st.cache_data  # Cache the data to avoid reloading on every rerun
def load_logo_data():
    with open("logo_icons.json", "r") as f:
        logo_data = json.load(f)
    return {item["name"]: item["logo"] for item in logo_data}


# Create logo dictionary (cached and shared across all cards)
logo_dict = load_logo_data()


# Function to encode the image as base64 and crop it if coordinates are provided
def get_cropped_image_base64(
    image_path, x1: int = None, y1: int = None, x2: int = None, y2: int = None
):
    image = Image.open(image_path)
    if x1 and y1 and x2 and y2:
        cropped_image = image.crop((x1, y1, x2, y2))
    else:
        cropped_image = image

    from io import BytesIO

    buffered = BytesIO()
    cropped_image.save(buffered, format="JPEG")
    encoded_string = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{encoded_string}"


# Function to encode an SVG file as a base64 data URI
def get_svg_base64(file_path):
    with open(file_path, "rb") as svg_file:
        encoded_string = base64.b64encode(svg_file.read()).decode()
    return f"data:image/svg+xml;base64,{encoded_string}"


# Define the trading card as an HTML template with Material Design style,
def trading_card(
    image_base64,
    make,
    model,
    year,
    text_color,
    link_url,
    drivetrain,
    class_type,
    cylinders,
    displacement,
    city_mpg,
    highway_mpg,
    fuel_type,
):
    # Get logo URL for the current vehicle make
    logo_url = logo_dict.get(make, None)

    # Generate logo HTML if available, with a slightly smaller container
    logo_html = ""
    if logo_url:
        logo_html = f"""
        <div class="logo-container">
            <img src="{logo_url}" alt="{make} logo" class="logo-image">
        </div>
        """

    # Get the drivetrain SVG icon as a data URI (using the light version)
    drivetrain_icon = get_svg_base64(f"./icons/{drivetrain}-dark.svg")

    # Build the specs section based on the fuel type
    if fuel_type.lower() == "electricity":
        specs_section = f"""
            <div class="specs-section">
                <div class="year">{year}</div>
                |
                <div class="drivetrain-info">
                    <img src="{drivetrain_icon}" alt="{drivetrain} layout" class="drivetrain-icon">
                    <span>{drivetrain.upper()}</span>
                </div>
            </div>
            <p>{fuel_type} {class_type}</p>
        """
    else:
        specs_section = f"""
            <div class="specs-section">
                <div class="year">{year}</div>
                |
                <div class="drivetrain-info">
                    <img src="{drivetrain_icon}" alt="{drivetrain} layout" class="drivetrain-icon">
                    <span>{drivetrain.upper()}</span>
                </div>
                |
                <div class="engine-info">
                    <span>{cylinders}-cyl &bull; {displacement}L</span>
                </div>
            </div>
            <p>{fuel_type} {class_type} - {(city_mpg + highway_mpg) / 2} MPG</p>
        """

    card_html = f"""
    <!-- Include Roboto font from Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        .card {{
            width: 300px;
            border-radius: 4px;
            overflow: hidden;
            background-color: #fff;
            box-shadow: 0 1px 3px {text_color}, 0 1px 2px {text_color};
            transition: box-shadow 0.3s ease-in-out;
            font-family: 'Roboto', sans-serif;
            position: relative;
            margin: 10px;
        }}
        .card:hover {{
            box-shadow: 0 8px 16px {text_color}, 0 6px 6px {text_color};
        }}
        .card img.main-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .card-text {{
            padding: 16px;
            color: {text_color};
        }}
        .card-text h3 {{
            margin: 0;
            font-size: 1.25rem;
            font-weight: 500;
        }}
        .card-text p {{
            margin: 8px 0 0;
            font-size: 0.875rem;
            color: #666;
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
            width: 40px;
            height: 40px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 4px;
            box-shadow: 0 2px 4px {text_color};
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}
        .logo-image {{
            max-width: 80%;
            max-height: 80%;
            object-fit: contain;
        }}
        .specs-section {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            margin: 12px 0;
            color: #333;
            font-size: 0.875rem;
        }}
        .drivetrain-info {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .drivetrain-icon {{
            width: 24px;
            height: auto;
        }}
    </style>
    <div class="card">
        <a href="{link_url}" target="_blank">
            <img src="{image_base64}" alt="Car image" class="main-image">
            {logo_html}
            <div class="card-text">
                <h3>{make} {model}</h3>
                {specs_section}
            </div>
        </a>
    </div>
    """
    return card_html
