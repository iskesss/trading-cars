import streamlit as st
from core import identify_vehicle

# Streamlit frontend
st.title("Car Identification App")
st.write("Upload an image of a car, and I'll identify its year, make, and model!")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    # Convert the uploaded file to bytes
    image_bytes = uploaded_file.getvalue()

    # Identify the car
    with st.spinner("Identifying the car..."):
        try:
            result = identify_vehicle(image_bytes)
            st.success(f"Identification Result: {result}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
