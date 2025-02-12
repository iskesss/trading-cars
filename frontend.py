import os
import uuid
import json
import streamlit as st
from core import identify_vehicle
from streamlit_card import card
from card import get_cropped_image_base64, trading_card

# Page configuration
st.set_page_config(page_title="TradingCars", layout="wide")

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


def add_car_page():
    st.title("Add a Car to Your Collection")
    st.write("Upload an image of a car to identify and add it to your collection.")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        image_bytes = uploaded_file.getvalue()

        if st.button("Identify and Add to Collection"):
            with st.spinner("Identifying the car..."):
                try:
                    result = identify_vehicle(image_bytes)

                    # Ensure result is in the correct format
                    if isinstance(result, (list, tuple)):
                        car_info = {
                            "year": str(result[0]) if len(result) > 0 else "Unknown",
                            "make": str(result[1]) if len(result) > 1 else "Unknown",
                            "model": str(result[2]) if len(result) > 2 else "Unknown",
                            "color": str(result[3]) if len(result) > 3 else "Unknown",
                            "x1": str(result[4]) if len(result) > 4 else "Unknown",
                            "y1": str(result[5]) if len(result) > 5 else "Unknown",
                            "x2": str(result[6]) if len(result) > 6 else "Unknown",
                            "y2": str(result[7]) if len(result) > 7 else "Unknown",
                        }
                    else:
                        car_info = result

                    # Save image
                    image_filename = f"{uuid.uuid4().hex}.png"
                    image_path = os.path.join(COLLECTION_DIR, image_filename)
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)

                    # Update metadata
                    metadata = load_metadata()
                    metadata[image_filename] = car_info
                    save_metadata(metadata)

                    st.success("Car successfully added to your collection!")
                    st.markdown(
                        f"""
                        **Identified as:**
                        - Year: {car_info.get('year', 'Unknown')}
                        - Make: {car_info.get('make', 'Unknown')}
                        - Model: {car_info.get('model', 'Unknown')}
                    """
                    )
                except Exception as e:
                    st.error(f"Error during identification: {str(e)}")


def gallery_page():
    st.title("Car Gallery")
    st.write("Your collection of identified cars")

    metadata = load_metadata()
    if metadata:
        cols = st.columns(2)
        # Keep track of valid entries to potentially clean up metadata
        valid_entries = {}

        for idx, (image_filename, details) in enumerate(metadata.items()):
            img_path = os.path.join(COLLECTION_DIR, image_filename)

            # Check if the image file exists
            if not os.path.exists(img_path):
                continue

            # Try to display the image and its details
            try:
                col = cols[idx % 2]
                with col:
                    st.markdown('<div class="car-card">', unsafe_allow_html=True)
                    with open(img_path, "rb") as img_file:
                        image_bytes = img_file.read()
                        st.image(image_bytes, use_container_width=True)
                    st.markdown(
                        f"<span style='color:{details.get('color','Unknown')}'>{details.get('year', 'Unknown')} "
                        f"{details.get('make', 'Unknown')} "
                        f"{details.get('model', 'Unknown')}</span>",
                        unsafe_allow_html=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                valid_entries[image_filename] = details
            except Exception as e:
                st.error(f"Error displaying image {image_filename}: {str(e)}")
                continue

        # Update metadata if some entries were invalid
        if len(valid_entries) != len(metadata):
            save_metadata(valid_entries)

    else:
        st.info("No cars in your collection yet. Add some cars to get started!")


# Sidebar navigation
st.sidebar.markdown(
    """
    # 🚗 TradingCars
    ___
"""
)

page = st.sidebar.radio(
    "Navigation", ("🔍 Add Car", "🖼️ Gallery"), label_visibility="collapsed"
)

if page == "🔍 Add Car":
    add_car_page()
elif page == "🖼️ Gallery":
    gallery_page()
