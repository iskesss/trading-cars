import base64
import json
import streamlit as st
from PIL import Image
from core import get_car_stats
import icecream as ic


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


def find_suitable_card(vehicle_image_path, vehicle_details):
    image_base64 = get_cropped_image_base64(
        image_path=vehicle_image_path,
        # x1=details.get("x1", "Unknown"), # bounding boxes not supported at the moment
        # y1=details.get("y1", "Unknown"), # bounding boxes not supported at the moment
        # x2=details.get("x2", "Unknown"), # bounding boxes not supported at the moment
        # y2=details.get("y2", "Unknown"), # bounding boxes not supported at the moment
    )

    curr_make = vehicle_details.get("make")
    curr_model = vehicle_details.get("model")
    curr_year = vehicle_details.get("year")
    curr_vehicle_color = vehicle_details.get("color")
    curr_link_url = ("https://google.com",)  # put something cool here

    curr_drivetrain = vehicle_details.get("drive", "Unknown")
    curr_class_type = vehicle_details.get("class", "Unknown")
    curr_cylinders = vehicle_details.get("cylinders", "Unknown")
    curr_displacement = vehicle_details.get("displacement", "Unknown")
    curr_fuel_type = vehicle_details.get("fuel_type", "Unknown")
    curr_city_mpg = vehicle_details.get("city_mpg", "Unknown")
    curr_highway_mpg = vehicle_details.get("highway_mpg", "Unknown")

    if (
        curr_drivetrain == "Unknown"
        or curr_displacement == "Unknown"
        or curr_city_mpg == "Unknown"
        or curr_highway_mpg == "Unknown"
        or curr_fuel_type == "Unknown"
        or curr_cylinders == "Unknown"
        or curr_class_type == "Unknown"
    ):
        try:
            card_html = basic_trading_card(
                image_base64=image_base64,
                make=curr_make,
                model=curr_model,
                year=curr_year,
                vehicle_color=curr_vehicle_color,
                link_url=curr_link_url,
            )
        except Exception as e:
            print(f"Error building basic card: {str(e)}")
    else:
        try:
            card_html = trading_card_with_specs(
                image_base64=image_base64,
                make=curr_make,
                model=curr_model,
                year=curr_year,
                vehicle_color=curr_vehicle_color,
                drivetrain=curr_drivetrain,
                link_url=curr_link_url,
                displacement=curr_displacement,
                city_mpg=curr_city_mpg,
                highway_mpg=curr_highway_mpg,
                fuel_type=curr_fuel_type,
                cylinders=curr_cylinders,
                class_type=curr_class_type,
            )
        except Exception as e:
            print(f"Error building card with specs: {str(e)}")
    return card_html


def basic_trading_card(
    image_base64,
    make: str,
    model: str,
    year: str,
    vehicle_color: str,
    link_url: str,
):
    # Get the logo URL for the given make (assuming logo_dict is defined globally)
    logo_url = logo_dict.get(make, None)
    logo_html = ""
    if logo_url:
        logo_html = f"""
        <div class="logo-container">
            <img src="{logo_url}" alt="{make} logo" class="logo-image">
        </div>
        """

    # Build the card HTML
    card_html = f"""
    <!-- Include Roboto font from Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        .card {{
            width: 300px;
            border-radius: 4px;
            overflow: hidden;
            background-color: #fff;
            box-shadow: 0 1px 3px {vehicle_color};
            transition: box-shadow 0.3s ease-in-out;
            font-family: 'Roboto', sans-serif;
            position: relative;
            margin: 10px;
        }}
        .card:hover {{
            box-shadow: 0 8px 16px {vehicle_color};
        }}
        .card img.main-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .card-text {{
            padding: 16px;
            color: #333;
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
            box-shadow: 0 2px 4px {vehicle_color};
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
    </style>
    <div class="card">
        <a href="{link_url}" target="_blank">
            <img src="{image_base64}" alt="Car image" class="main-image">
            {logo_html}
            <div class="card-text">
                <h3>{make} {model}</h3>
                <p>{year}</p>
            </div>
        </a>
    </div>
    """
    return card_html


def trading_card_with_specs(
    image_base64,
    make: str,
    model: str,
    year: str,
    vehicle_color: str,
    link_url: str,
    drivetrain: str,
    class_type: str,
    cylinders: str,
    displacement: str,
    city_mpg: str,
    highway_mpg: str,
    fuel_type: str,
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

    # Get the drivetrain SVG icon as a data URI (using the dark version)
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
            <p>{fuel_type} - {class_type}</p>
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
            <p>{fuel_type} - {class_type} - {(city_mpg + highway_mpg) / 2} MPG</p>
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
            box-shadow: 0 1px 3px {vehicle_color}, 0 1px 2px {vehicle_color};
            transition: box-shadow 0.3s ease-in-out;
            font-family: 'Roboto', sans-serif;
            position: relative;
            margin: 10px;
        }}
        .card:hover {{
            box-shadow: 0 8px 16px {vehicle_color}, 0 6px 6px {vehicle_color};
        }}
        .card img.main-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .card-text {{
            padding: 16px;
            color: {vehicle_color};
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
            box-shadow: 0 2px 4px {vehicle_color};
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
