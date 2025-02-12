import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


def identify_vehicle(image_bytes):
    # returns "(YEAR,MAKE,MODEL,COLOR)" 4-tuple

    genai.configure(api_key=os.environ["GOOGLE_AI_API"])

    # Initialize model with system instruction
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction="You are a car recognition expert. Respond ONLY with 'YEAR, MAKE, MODEL, PRIMARY_COLOR_HEX_CODE' of the main car in the photo.",
    )

    # Generate content with separate text and image parts
    response = model.generate_content(
        [
            "Identify this car in format: 'YEAR, MAKE, MODEL, PRIMARY_COLOR_HEX_CODE'",
            {"mime_type": "image/jpeg", "data": image_bytes},
        ]
    )
    year, make, model, color_code = map(str.strip, response.text.split(","))

    return (year, make, model, color_code)
