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
            width: 50px; /* Fixed container size */
            height: 50px; /* Fixed container size */
            background: rgba(255, 255, 255, 0.9);
            border-radius: 50%;
            padding: 3px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden; /* Ensures the logo doesn't spill out */
        }}
        .logo-image {{
            max-width: 100%; /* Constrains logo to container width */
            max-height: 100%; /* Constrains logo to container height */
            object-fit: contain; /* Ensures the logo fits nicely */
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


# Streamlit app
def main():
    st.title("Car Trading Card")

    # Inputs for customization
    image_path = st.text_input("Enter the local image path", "car.jpg")
    x1 = st.slider("Crop X1", 0, 1000, 100)
    y1 = st.slider("Crop Y1", 0, 1000, 100)
    x2 = st.slider("Crop X2", 0, 1000, 400)
    y2 = st.slider("Crop Y2", 0, 1000, 300)
    make = st.text_input("Make", "Tesla")
    model = st.text_input("Model", "Model S")
    year = st.text_input("Year", "2023")
    text_color = st.color_picker("Text color", "#000000")
    link_url = st.text_input("Link URL", "https://www.tesla.com")

    # Ensure x2 > x1 and y2 > y1
    if x2 <= x1 or y2 <= y1:
        st.error(
            "Invalid crop coordinates: x2 must be greater than x1, and y2 must be greater than y1."
        )
        return

    # Encode the cropped image as base64
    try:
        image_base64 = get_cropped_image_base64(image_path, x1, y1, x2, y2)
    except FileNotFoundError:
        st.error("Image file not found. Please check the path.")
        return
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return

    # Generate and display the card
    card_html = trading_card(image_base64, make, model, year, text_color, link_url)
    st.components.v1.html(card_html, height=300)


if __name__ == "__main__":
    main()
