import pytesseract
from PIL import Image
import os

def extract_text_from_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text
