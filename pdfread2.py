import os
import cv2
import pytesseract
from pdf2image import convert_from_path
import numpy as np

# Set Tesseract path if needed (Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def remove_lines(image):
    """Remove hand-drawn horizontal and vertical lines from image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)

    # Detect horizontal lines
    horizontal_kernel = np.ones((1, 25), np.uint8)
    horizontal_lines = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Detect vertical lines
    vertical_kernel = np.ones((25, 1), np.uint8)
    vertical_lines = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Combine all lines and subtract from original
    all_lines = cv2.add(horizontal_lines, vertical_lines)
    cleaned = cv2.subtract(inverted, all_lines)
    final = cv2.bitwise_not(cleaned)

    return final

def extract_text_from_pdf(pdf_path):
    print(f"📄 Converting PDF to image(s)...")
    pages = convert_from_path(pdf_path, dpi=300)

    all_text = ""
    for i, page in enumerate(pages):
        image_path = f"page_{i + 1}.png"
        cleaned_path = f"cleaned_page_{i + 1}.png"

        # Save original image
        page.save(image_path, "PNG")

        # Read and clean lines
        img = cv2.imread(image_path)
        cleaned_img = remove_lines(img)

        # Save cleaned image (optional)
        cv2.imwrite(cleaned_path, cleaned_img)

        # OCR on cleaned image
        print(f"🔍 OCR on cleaned image: {cleaned_path}")
        text = pytesseract.image_to_string(cleaned_img)
        all_text += f"\n===== Page {i + 1} =====\n{text}"

        # Optional: delete intermediate image files
        os.remove(image_path)
        os.remove(cleaned_path)

    return all_text

# === Run the OCR pipeline ===
pdf_file = "samples/Doc_2781.pdf"  # Replace with your PDF file path
output_text = extract_text_from_pdf(pdf_file)

print("\n\n===== Final OCR Output =====\n")
print(output_text)
