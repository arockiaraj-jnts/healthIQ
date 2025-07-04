import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import os
from utils import extract_urine_routine_data,extract_stool_routine_data,extract_lipid_profile_data,extract_glucose_data,extract_thyroid_data


# === Step 1: Convert PDF to Images ===
def convert_pdf_to_images(pdf_path, dpi=300):
    images = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    for i, img in enumerate(images):
        img_path = f"page_{i+1}.png"
        img.save(img_path, 'PNG')
        image_paths.append(img_path)
    return image_paths

# === Step 2: Check Image Resolution ===
def check_resolution(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        print(f"📐 Resolution: {width}x{height}")
        if width < 1000 or height < 1000:
            print("⚠️ Warning: Low resolution - OCR accuracy may suffer.")
        else:
            print("✅ Resolution is good for OCR.")

# === Step 3: OCR with Tesseract ===
def extract_text_with_tesseract(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    print("\n OCR Result:")
    print(text.strip())
    report_name=get_report_name(text.strip()).replace('&','')
    print(report_name)
    report_handlers = {
    "Urine Routine": lambda: extract_urine_routine_data(text.strip(), report_name),
    "Stool Routine": lambda: extract_stool_routine_data(text.strip(), report_name),
    "Lipid Profile": lambda: extract_lipid_profile_data(text.strip(), report_name),
    "glucose fasting  postprandial": lambda: extract_glucose_data(text.strip(), report_name),
    "Thyroid Function Test": lambda: extract_thyroid_data(text.strip(), report_name),
    }

    json_output = report_handlers.get(report_name, lambda: {"error": "Unknown report"})()
    
    print(json_output)




# === Main Function ===
def process_pdf(pdf_path):
    print(f"📄 Processing PDF: {pdf_path}")
    image_paths = convert_pdf_to_images(pdf_path)

    for image_path in image_paths:
        #if image_path!='page_7.png':
         #   continue
        print(f"\n--- Processing {image_path} ---")
        check_resolution(image_path)
        #check_for_hand_drawn_lines(image_path)
        ###extract_text_with_tesseract(image_path)
        ###os.remove(image_path)  # Cleanup after processing
        

def get_report_name(ocr_text):
    known_reports = [
        "Urine Routine", "Complete Blood Count", "CBC", "Liver Function Test",
        "Thyroid Function Test", "Blood Sugar", "Lipid Profile", "Kidney Function Test",
        "Urine Culture", "Stool Routine", "Hematology", "Blood Test", "glucose fasting & postprandial"
    ]
    #, "glucose fasting & postprandial"

    lines = ocr_text.splitlines()
    clean_lines = [line.strip().lower() for line in lines if line.strip()]  # normalize to lowercase

    # Step 1: Match against known report names
    for line in clean_lines[:20]:
        for report in known_reports:
            if report.lower() in line:
                return report  # return original casing from list

    # Step 2: Heuristic fallback — standalone lines with title case
    for line in lines:
        clean_line = line.strip()
        if (
            clean_line.istitle() and
            1 <= len(clean_line.split()) <= 4 and
            ':' not in clean_line and
            not any(word in clean_line.lower() for word in ['name', 'date', 'patient', 'age'])
        ):
            return clean_line

    return "Unknown Report"


def check_for_hand_drawn_lines(image):
        """Detect horizontal/vertical lines that may be hand-drawn. Return True if found."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)

        # Kernels to detect long lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))

        detected_horizontal = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        detected_vertical = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

        # Combine and find contours
        combined = cv2.add(detected_horizontal, detected_vertical)
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 30 or h > 30:  # Skip small noise
                return True  # Line detected

        return False  # No suspicious lines
       

# === Entry Point ===
if __name__ == "__main__":
    pdf_file_path = "samples/doc1.pdf"  # Replace with your actual PDF path
    #pdf_file_path = "samples/Doc_1614.pdf" 
    #pdf_file_path = "samples/Doc_2781.pdf"  # Replace with your actual PDF path
    process_pdf(pdf_file_path)
