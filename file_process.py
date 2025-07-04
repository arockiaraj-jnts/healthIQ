import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
from datetime import datetime
from utils_web import extract_glucose_data,extract_thyroid_data,extract_lipid_profile_data
def process_pdf(pdf_path,output_folder):
    print(f" Processing PDF: {pdf_path}")
    image_paths = convert_pdf_to_images(pdf_path,output_folder)
    all_extract_data=[]
    for image_path in image_paths:
        #if image_path!='page_7.png':
         #   continue
        print(f"\n--- Processing {image_path} ---")
        image = Image.open(image_path).convert("RGB")
        output_path = datetime.now().strftime("%d%m%y%H%M%S")
        output_pdf_path = os.path.join(output_folder, f"{output_path}.pdf")
        image = Image.open(image_path).convert("RGB")
        image.save(output_pdf_path, "PDF")        
        check_resolution(image_path)
        #check_for_hand_drawn_lines(image_path)
        extract_data= extract_text_with_tesseract(image_path,output_pdf_path)
        os.remove(image_path)  # Cleanup after processing
        all_extract_data.append(extract_data)
    print("*********")  
    
    #print(all_extract_data) 
    return  all_extract_data  

# === Step 1: Convert PDF to Images ===
def convert_pdf_to_images(pdf_path, output_folder, dpi=300):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    for i, img in enumerate(images):
        img_filename = f"page_{i+1}.png"
        img_path = os.path.join(output_folder, img_filename)
        img.save(img_path, 'PNG')
        image_paths.append(img_path)

    return image_paths

# === Step 2: Check Image Resolution ===
def check_resolution(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        print(f" Resolution: {width}x{height}")
        if width < 1000 or height < 1000:
            return " Warning: Low resolution - OCR accuracy may suffer.",False
        else:
            return " Resolution is good for OCR.",True

# === Step 3: OCR with Tesseract ===
def extract_text_with_tesseract(image_path,output_pdf_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    print("\n OCR Result:")
    #print(text.strip())
    report_name=get_report_name(text.strip()).replace('&','')
    print(report_name)
    report_handlers = {
    #"Urine Routine": lambda: extract_urine_routine_data(text.strip(), report_name),
    #"Stool Routine": lambda: extract_stool_routine_data(text.strip(), report_name),
    "Lipid Profile": lambda: extract_lipid_profile_data(text.strip(), report_name,output_pdf_path),
    "glucose fasting  postprandial": lambda: extract_glucose_data(text.strip(), report_name,output_pdf_path),
    "Thyroid Function Test": lambda: extract_thyroid_data(text.strip(), report_name,output_pdf_path),
    }

    json_output = report_handlers.get(report_name, lambda: {"error": "Unknown report"})()
    
    
    print(json_output)  
    return json_output

def get_report_name(ocr_text):
    known_reports = [
        "Urine Routine", "Complete Blood Count", "CBC", "Liver Function Test",
        "Thyroid Profile", "Blood Sugar", "Lipid Profile", "Kidney Function Test",
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