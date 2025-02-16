import streamlit as st
import os
import uuid
import json
from core import identify_vehicle, get_car_stats

# Get port from environment variable
PORT = int(os.getenv("PORT", "8080"))
# Page configuration
st.set_page_config(page_title="CarCollector", layout="wide", port=PORT)

# Directory and file setup
COLLECTION_DIR = "car_collection"
METADATA_FILE = os.path.join(COLLECTION_DIR, "metadata.json")

if not os.path.exists(COLLECTION_DIR):
    os.makedirs(COLLECTION_DIR)

if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "w") as f:
        json.dump({}, f)


def load_metadata():
    with open(METADATA_FILE, "r") as f:
        return json.load(f)


def save_metadata(metadata):
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=4)


# Load logo data once at the start (outside the function)
@st.cache_data  # Cache the data to avoid reloading on every rerun
def load_logo_data():
    with open("logo_icons.json", "r") as f:
        logo_data = json.load(f)
    return {item["name"]: item["logo"] for item in logo_data}


def main_page():
    from card import find_suitable_card

    # Inject CSS to import the Roboto font and force it on all app elements
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
        /* Target the main container and all of its children */
        [data-testid="stAppViewContainer"] * {
            font-family: 'Roboto', sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("CarCollector")
    uploaded_file = st.file_uploader(
        "Add a car to your collection....",
        type=["jpg", "jpeg"],
    )
    if uploaded_file:
        image_bytes = uploaded_file.getvalue()
        with st.spinner("Identifying the car...", show_time=True):
            try:
                result = identify_vehicle(image_bytes)

                # Ensure result is in the correct format
                if isinstance(result, (list, tuple)):
                    car_info = {
                        "year": str(result[0]) if len(result) > 0 else "Unknown",
                        "make": str(result[1]) if len(result) > 1 else "Unknown",
                        "model": str(result[2]) if len(result) > 2 else "Unknown",
                        "color": str(result[3]) if len(result) > 3 else "Unknown",
                        # "x1": result[4] if len(result) > 4 else "Unknown", # bounding boxes not yet implemented
                        # "y1": result[5] if len(result) > 5 else "Unknown", # bounding boxes not yet implemented
                        # "x2": result[6] if len(result) > 6 else "Unknown", # bounding boxes not yet implemented
                        # "y2": result[7] if len(result) > 7 else "Unknown", # bounding boxes not yet implemented
                    }
                    api_stats = get_car_stats(  # uses year, make, and model to fetch api_stats from Ninja Api
                        make=car_info.get("make", "Unknown"),
                        model=car_info.get("model", "Unknown"),
                        year=car_info.get("year", "Unknown"),
                    )
                    # remove year, make, and model from api_stats before merging with car_info
                    for key in ["year", "make", "model"]:
                        api_stats.pop(key, None)
                    car_info.update(api_stats)  # merge car_info and car_stats
                else:
                    car_info = result
                # Save image
                image_filename = f"{uuid.uuid4().hex}.png"
                image_path = os.path.join(COLLECTION_DIR, image_filename)
                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                # Update metadata
                metadata = load_metadata()
                metadata[image_filename] = car_info  # save car_info to disk
                save_metadata(metadata)

                st.success(
                    f"{car_info.get('year', 'YearUnknown')} {car_info.get('make', 'MakeUnknown')} {car_info.get('model', 'ModelUnknown')} successfully added to your collection!"
                )

            except Exception as e:
                st.error(f"Error during identification: {str(e)}")

    metadata = load_metadata()

    if metadata:

        cols = st.columns(3)

        for idx, (image_filename, details) in enumerate(
            reversed(list(metadata.items()))  # newest cars appear first in gallery
        ):

            image_path = os.path.join(COLLECTION_DIR, image_filename)

            # Check if the image file exists
            if not os.path.exists(image_path):
                continue

            try:
                col = cols[idx % 3]
                with col:
                    card_html = find_suitable_card(
                        vehicle_image_path=image_path, vehicle_details=details
                    )
                    st.components.v1.html(card_html, height=350)

            except Exception as e:
                st.error(f"Error displaying card {image_filename}: {str(e)}")
                continue

    else:
        st.info("No cars in your collection yet. Add some cars to get started!")


main_page()
