import cv2
from PIL import Image
from PIL.ExifTags import TAGS

def check_if_mobile_photo(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return False, "No EXIF data found – possibly not a mobile photo"

        details = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            details[tag] = value

        camera_model = details.get("Model", "Unknown")
        make = details.get("Make", "Unknown")

        if any(keyword in (camera_model + make).lower() for keyword in ['iphone', 'samsung', 'pixel', 'oneplus', 'xiaomi', 'redmi', 'vivo', 'realme', 'oppo']):
            return True, f"Mobile photo detected: {make} {camera_model}"
        return False, f"Camera: {make} {camera_model}"
    except Exception as e:
        return False, f"EXIF read error: {e}"

def is_blurry(image_path, threshold=100.0):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return True, 0.0
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    return laplacian_var < threshold, laplacian_var

def check_background_uniformity(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return True, 0.0
    h, w = img.shape
    corners = [img[0:50, 0:50], img[0:50, -50:], img[-50:, 0:50], img[-50:, -50:]]
    brightness = [corner.mean() for corner in corners]
    variation = max(brightness) - min(brightness)
    return variation > 30, variation

def is_probably_mobile_photo(path):
    exif_result, exif_msg = check_if_mobile_photo(path)
    blurry, sharpness = is_blurry(path)
    uneven, light_diff = check_background_uniformity(path)

    score = sum([exif_result, blurry, uneven])
    if score >= 2:
        return True, f"Likely mobile photo | {exif_msg}, Blur: {sharpness:.2f}, Lighting Var: {light_diff:.2f}"
    return False, f"Likely scanned image | {exif_msg}, Blur: {sharpness:.2f}, Lighting Var: {light_diff:.2f}"

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python detect_mobile_photo.py <image_path>")
    else:
        image_path = sys.argv[1]
        result, reason = is_probably_mobile_photo(image_path)
        print("\n📸 Result:", "MOBILE PHOTO" if result else "SCANNED DOCUMENT")
        print("Details:", reason)