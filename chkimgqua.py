from PIL import Image

img = Image.open("samples/ClinicalPathology_urineRoutine.jpeg")
dpi = img.info.get('dpi', (72, 72))  # Default if not set
print(f"DPI: {dpi}")  # Should be at least (300, 300)
