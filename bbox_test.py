import cv2
import json
import os


def draw_bounding_boxes():
    # Read metadata
    collection_dir = "car_collection"
    metadata_path = os.path.join(collection_dir, "metadata.json")

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    # Process each image
    for image_filename, details in metadata.items():
        # Construct full image path
        image_path = os.path.join(collection_dir, image_filename)

        # Read image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Could not read image: {image_path}")
            continue

        # Get bounding box coordinates
        x1 = int(details["x1"])
        y1 = int(details["y1"])
        x2 = int(details["x2"])
        y2 = int(details["y2"])

        # Draw rectangle
        color = (0, 255, 0)  # Green in BGR
        thickness = 2
        cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

        # Add label
        label = f"{details['year']} {details['make']} {details['model']}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        text_color = (255, 255, 255)  # White
        cv2.putText(img, label, (x1, y1 - 10), font, font_scale, text_color, thickness)

        # Save the annotated image
        output_path = os.path.join(collection_dir, f"annotated_{image_filename}")
        cv2.imwrite(output_path, img)
        print(f"Saved annotated image to: {output_path}")


if __name__ == "__main__":
    draw_bounding_boxes()
