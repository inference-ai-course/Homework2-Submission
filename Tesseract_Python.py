from PIL import Image
import pytesseract
import os

# === Configuration ===
# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\X380\scoop\shims\tesseract.exe"

# Set the tessdata environment variable (so Tesseract can find language files)
os.environ['TESSDATA_PREFIX'] = r"C:\Users\X380\scoop\persist\tesseract"

# === OCR Processing ===
# Load the image
image = Image.open(r"D:\MLE\Homework2-Submission\test_image.jpg")

# Perform OCR (English)
text = pytesseract.image_to_string(image, lang='eng')

# Print the recognized text
print(text)
