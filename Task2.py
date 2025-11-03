import os
import json
import requests
from tqdm import tqdm
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from io import BytesIO

# Setup
os.makedirs("pdf_ocr", exist_ok=True)

with open("arxiv_clean_task2.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

# Helper Functions

def download_pdf(url, save_path):
    """Download arXiv PDF given the /abs/ URL."""
    pdf_url = url.replace("/abs/", "/pdf/") + ".pdf"
    r = requests.get(pdf_url, stream=True)
    if r.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(r.content)
        return True
    return False

def pdf_to_text(pdf_path):
    """Convert a PDF to text via OCR."""
    text_output = []
    # Convert each page to image
    pages = convert_from_path(pdf_path, dpi=300)
    for page_img in pages:
        text = pytesseract.image_to_string(page_img)
        text_output.append(text)
    return "\n".join(text_output)

# Main OCR Loop

for paper in tqdm(papers, desc="Processing PDFs"):
    arxiv_id = paper["url"].split("/")[-1]
    pdf_path = f"pdf_ocr/{arxiv_id}.pdf"
    txt_path = f"pdf_ocr/{arxiv_id}.txt"

    # Skip existing files
    if os.path.exists(txt_path):
        continue

    try:
        # Download PDF
        if not os.path.exists(pdf_path):
            success = download_pdf(paper["url"], pdf_path)
            if not success:
                print(f"Failed to download: {paper['url']}")
                continue

        # OCR
        text = pdf_to_text(pdf_path)

        # Save text
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

    except Exception as e:
        print(f"Error processing {arxiv_id}: {e}")