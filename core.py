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

    # parse LLM response
    (
        year,
        make,
        model,
        color_code,
    ) = map(str.strip, response.text.split(","))

    return (
        year,
        make,
        model,
        color_code,
    )


def identify_vehicle_with_bbox(image_bytes):
    # returns "(YEAR,MAKE,MODEL,COLOR)" 4-tuple

    genai.configure(api_key=os.environ["GOOGLE_AI_API"])

    # Initialize model with system instruction
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction="""
You are a car recognition expert. Your response must consist solely of two distinct 4-tuples describing the main car in the image.
Firstly (YEAR, MAKE, MODEL, PRIMARY_COLOR_HEX_CODE) and then secondly, upperleft/lowerright bounding box corner coordinates surrounding the entire car, in the tuple form (x1, y1, x2, y2).""",
    )

    # Generate content with separate text and image parts
    response = model.generate_content(
        [
            "Identify this car in format: (YEAR, MAKE, MODEL, PRIMARY_COLOR_HEX_CODE), (x1, y1, x2, y2).",
            {"mime_type": "image/jpeg", "data": image_bytes},
        ]
    )

    print(response.text)

    # Parse LLM response
    try:
        # Split the response into the two tuples
        tuple1, tuple2 = response.text.strip("()").split("), (")

        # Extract values from the first tuple (YEAR, MAKE, MODEL, PRIMARY_COLOR_HEX_CODE)
        year, make, model, color_code = map(str.strip, tuple1.split(","))

        # Extract values from the second tuple (x1, y1, x2, y2)
        x1, y1, x2, y2 = map(str.strip, tuple2.strip("()").split(","))

        # Convert coordinates to integers
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # Validate bounding box coordinates
        if x2 <= x1 or y2 <= y1:
            print(
                "LLM provided invalid crop coordinates! x2 must be greater than x1, and y2 must be greater than y1."
            )
            return (
                year,
                make,
                model,
                color_code,
            )

        return (
            year,
            make,
            model,
            color_code,
            x1,
            y1,
            x2,
            y2,
        )

    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return None
