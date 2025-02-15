import os
import uuid
import json
import streamlit as st
from core import identify_vehicle, get_car_stats
from card import get_cropped_image_base64, trading_card

# Page configuration
st.set_page_config(page_title="Trading Cars", layout="wide")

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


def main_page():
    st.title("Trading Cars")
    # st.write("Add a car to your collection!")
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

            # Try to display the image and its details
            try:
                col = cols[idx % 3]
                with col:
                    image_base64 = get_cropped_image_base64(
                        image_path=image_path,
                        # x1=details.get("x1", "Unknown"), # bounding boxes not supported at the moment
                        # y1=details.get("y1", "Unknown"), # bounding boxes not supported at the moment
                        # x2=details.get("x2", "Unknown"), # bounding boxes not supported at the moment
                        # y2=details.get("y2", "Unknown"), # bounding boxes not supported at the moment
                    )

                    card_html = trading_card(
                        image_base64=image_base64,
                        make=details.get("make", "Unknown"),
                        model=details.get("model", "Unknown"),
                        year=details.get("year", "Unknown"),
                        text_color=details.get("color", "Unknown"),
                        drivetrain=details.get("drive", "Unknown"),
                        link_url="https://google.com",
                    )

                    st.components.v1.html(card_html, height=350)

                # valid_entries[image_filename] = details
            except Exception as e:
                st.error(f"Error displaying image {image_filename}: {str(e)}")
                continue

    else:
        st.info("No cars in your collection yet. Add some cars to get started!")


main_page()
