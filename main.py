from PIL import Image
import pytesseract #pip install pytesseract first
import fitz  # PyMuPDF - pip install PyMuPDF first
import io

# Load a PDF file
pdf_path = 'test_document.pdf'
pdf_document = fitz.open(pdf_path)

print(f"PDF loaded successfully: {pdf_path}")
print(f"Number of pages: {pdf_document.page_count}")

# Convert PDF pages to images and perform OCR
text = ""
for page_num in range(pdf_document.page_count):
    page = pdf_document[page_num]
    # Convert page to image
    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    
    # Convert to PIL Image
    img = Image.open(io.BytesIO(img_data))
    
    # Perform OCR on the image
    page_text = pytesseract.image_to_string(img)
    text += page_text

pdf_document.close()

with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(text)