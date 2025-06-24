import fitz  # PyMuPDF

def extract_images_with_dpi(pdf_path):
    doc = fitz.open(pdf_path)
    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)

        print(f"Page {page_index + 1} has {len(image_list)} image(s)")

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            dpi_x, dpi_y = base_image.get("dpi", (None, None))

            print(f"  → Image {img_index + 1}:")
            print(f"     DPI: {dpi_x} x {dpi_y}")
            print(f"     Size: {base_image['width']}x{base_image['height']}")
            print(f"     Format: {base_image['ext']}")
            print()
            
            # Optional: Save image
            # with open(f"image_{page_index+1}_{img_index+1}.{base_image['ext']}", "wb") as f:
            #     f.write(base_image["image"])


            image_width_px=base_image['width']
            image_height_px= base_image['height']
            page_width_in=8.27
            page_height_in=11.69
            dpi_x = image_width_px / page_width_in
            dpi_y = image_height_px / page_height_in
            print(round(dpi_x))
            print(round(dpi_y))

extract_images_with_dpi("samples/Doc_2781.pdf")
