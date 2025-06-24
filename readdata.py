import cv2
import pytesseract
import re

# Load and preprocess image
img = cv2.imread('samples/ClinicalPathology_urineRoutine.jpeg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ocr_result = pytesseract.image_to_string(gray)

# Debug: print full OCR output
print("===== OCR OUTPUT =====")
print(ocr_result)

# Extract lines that look like test data
lines = ocr_result.split('\n')
parsed_data = []

for line in lines:
    line = line.strip()
    if not line:
        continue

    # Try to extract reference range in brackets (if any)
    ref_match = re.search(r'\(([^()]+)\)', line)
    reference = ref_match.group(1).strip() if ref_match else ''

    # Remove reference from line
    clean_line = re.sub(r'\([^()]+\)', '', line)

    # Split remaining line into parts
    parts = re.split(r'\s{2,}|\t+', clean_line.strip())
    
    if len(parts) >= 2:
        test_name = parts[0].strip()
        result = parts[1].strip()
        parsed_data.append((test_name, result, reference))

# Output result
print("\n===== Parsed Test Data =====")
for test in parsed_data:
    print(test)
