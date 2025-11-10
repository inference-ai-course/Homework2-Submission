

# pytesseract.pytesseract.tesseract_cmd = r"d:\Tesseract-OCR\tesseract.exe"

import os
import re
import json
import requests
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm

# =============== Configuration ===============
json_path = r"D:\MLE\Homework2-Submission\arxiv_clean.json"
pdf_folder = r"D:\MLE\Homework2-Submission\pdfs"
txt_folder = r"D:\MLE\Homework2-Submission\pdf_ocr"
error_log = r"D:\MLE\Homework2-Submission\ocr_errors.txt"

os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(txt_folder, exist_ok=True)


pytesseract.pytesseract.tesseract_cmd = r"d:\Tesseract-OCR\tesseract.exe"


# =============== Functions ===============
def safe_filename(name: str) -> str:
    """Clean invalid characters, newlines, and spaces from filenames"""
    name = name.replace("\n", " ").replace("\r", " ").strip()
    return re.sub(r'[<>:"/\\|?*]+', '_', name)[:150]  # Avoid overly long filenames


def download_pdf(paper):
    """Download PDF from arXiv"""
    title = safe_filename(paper.get("title", "untitled"))
    pdf_path = os.path.join(pdf_folder, f"{title}.pdf")
    url = paper.get("pdf_url") or paper.get("url") or ""

    if os.path.exists(pdf_path):
        return pdf_path  # Already exists

    # Extract arXiv ID from URL
    m = re.search(r'arxiv\.org/(abs|pdf)/([0-9]+\.[0-9]+)', url)
    arxiv_id = m.group(2) if m else None
    if not arxiv_id:
        return None

    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    try:
        r = requests.get(pdf_url, timeout=20)
        if r.headers.get("Content-Type", "").lower().startswith("application/pdf"):
            with open(pdf_path, "wb") as f:
                f.write(r.content)
            return pdf_path
        else:
            with open(error_log, "a", encoding="utf-8") as logf:
                logf.write(f"❌ Not a PDF: {title} ({pdf_url})\n")
            return None
    except Exception as e:
        with open(error_log, "a", encoding="utf-8") as logf:
            logf.write(f"❌ Download failed: {title}\t{e}\n")
        return None


def pdf_to_text(pdf_path, txt_path):
    try:
        poppler_path = r"D:\poppler-25.07.0\Library\bin"
        pages = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
        text_all = []
        for page in pages:
            text = pytesseract.image_to_string(page, lang="eng", config="--psm 1")
            text_all.append(text)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(text_all))
        return True
    except Exception as e:
        with open(error_log, "a", encoding="utf-8") as logf:
            logf.write(f"❌ OCR失败 {pdf_path}\t{e}\n")
        return False


# =============== MAIN LOGIC ===============
with open(json_path, "r", encoding="utf-8") as f:
    papers = json.load(f)

print(f"Loaded {len(papers)} papers, starting download...")

success_dl, fail_dl = 0, 0
for paper in tqdm(papers, desc="Downloading PDFs"):
    pdf_path = download_pdf(paper)
    if pdf_path:
        success_dl += 1
    else:
        fail_dl += 1

print(f"\n✅ Download complete: {success_dl} succeeded, {fail_dl} failed.")

print("\nStarting OCR processing...")

success_ocr, fail_ocr = 0, 0
pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]

for pdf_file in tqdm(pdf_files, desc="OCR Processing PDFs"):
    pdf_path = os.path.join(pdf_folder, pdf_file)
    txt_path = os.path.join(txt_folder, os.path.splitext(pdf_file)[0] + ".txt")

    if pdf_to_text(pdf_path, txt_path):
        success_ocr += 1
    else:
        fail_ocr += 1

print(f"\n✅ OCR complete: {success_ocr} succeeded, {fail_ocr} failed.")
