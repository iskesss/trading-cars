import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


def identify_vehicle() -> str:
    # returns "(YEAR,MAKE,MODEL)" 3
    # Configure the API
    genai.configure(api_key=os.environ["GOOGLE_AI_API"])

    # Initialize model with system instruction
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction="You are a car recognition expert. Respond ONLY with 'YEAR, MAKE, MODEL' format.",
    )

    # Read image bytes
    with open("car.jpeg", "rb") as f:
        image_bytes = f.read()

    # Generate content with separate text and image parts
    response = model.generate_content(
        [
            "Identify this car in format: 'YEAR, MAKE, MODEL'",
            {"mime_type": "image/jpeg", "data": image_bytes},
        ]
    )
    year, make, model = map(str.strip, response.text.split(","))

    return (year, make, model)


print(identify_vehicle())
