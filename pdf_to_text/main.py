from PIL import Image
import pytesseract #pip install pytesseract first
from pdf2image import convert_from_path  # pip install pdf2image; requires Poppler
import io

# Load a PDF file
pdf_path = 'test_document.pdf'

print(f"PDF loaded successfully: {pdf_path}")

# Convert PDF pages to images using pdf2image (uses Poppler)
# Increase dpi for better OCR quality
images = convert_from_path(pdf_path, dpi=300)
print(f"Number of pages: {len(images)}")

# Perform OCR on each image
text = ""
for img in images:
    page_text = pytesseract.image_to_string(img)
    text += page_text

with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(text)