"""
arxiv_pdf_ocr.py

Brief description:
    Batch downloads PDFs from arXiv, performs Optical Character Recognition (OCR) on each page,
    and saves the extracted text to disk.

Detailed description:
    - Reads a JSON file containing metadata for arXiv papers, including PDF URLs.
    - Downloads each PDF with retry logic to handle transient network errors.
    - Validates that the downloaded file is a proper PDF and contains pages.
    - Converts each page of the PDF into an image at a configurable DPI.
    - Runs Tesseract OCR on each page image to extract text.
    - Saves the extracted text to a uniquely named .txt file in the output directory.
    - Uses multiprocessing to process multiple PDFs in parallel.
    - Logs only errors from worker processes and periodic progress updates.

Usage:
    python arxiv_pdf_ocr.py

Environment variables (optional):
    PROCESSED_TASKS_FOLDER - Folder containing processed tasks (default: "02_processed_tasks")
    PDF_OCR_FOLDER         - Subfolder for OCR text output (default: "pdf_ocr")
    ARXIV_JSON_FILE        - Name of JSON file with paper metadata (default: "arxiv_clean.json")
    OCR_DPI                - DPI for PDF-to-image conversion (default: 150)
    OCR_LANG               - Tesseract OCR language code (default: "eng")
    OCR_PSM                - Tesseract page segmentation mode (default: 6)
    REQUEST_TIMEOUT        - HTTP request timeout in seconds (default: 30)

Dependencies:
    - requests
    - pdf2image
    - pytesseract
    - Pillow (via pdf2image)
"""

import hashlib
import json
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse

import pytesseract
import requests
from pdf2image import convert_from_bytes, pdfinfo_from_bytes
from requests.adapters import HTTPAdapter, Retry

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

PROCESSED_TASKS_FOLDER = os.getenv("PROCESSED_TASKS_FOLDER", "02_processed_tasks")
PDF_OCR_FOLDER = os.getenv("PDF_OCR_FOLDER", "pdf_ocr")
ARXIV_JSON_FILE = os.getenv("ARXIV_JSON_FILE", "arxiv_clean.json")
OCR_DPI = int(os.getenv("OCR_DPI", "150"))
OCR_LANG = os.getenv("OCR_LANG", "eng")
OCR_PSM = int(os.getenv("OCR_PSM", "6"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"],
)
session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))


def process_paper_worker(
    paper: dict, index: int, total: int, output_dir: Path
) -> Tuple[int, bool, str]:
    """
    Worker function to process a single arXiv paper.

    Steps:
        1. Validate that the paper has a PDF URL.
        2. Generate a unique output filename based on the PDF URL.
        3. Download the PDF and validate its format.
        4. Extract the number of pages from the PDF.
        5. Convert each page to an image and run OCR.
        6. Save the extracted text to a .txt file.

    Args:
        paper (dict): Metadata for the paper, including 'title' and 'pdf_url'.
        index (int): The 1-based index of this paper in the batch.
        total (int): The total number of papers being processed.
        output_dir (Path): Directory where OCR results will be saved.

    Returns:
        Tuple[int, bool, str]:
            - index: The paper's index in the batch.
            - success: True if OCR succeeded or file was skipped, False on error.
            - message: Error message if failed, empty string otherwise.
    """
    title = paper.get("title", f"paper_{index}")
    pdf_url = paper.get("pdf_url")
    if not pdf_url:
        return index, False, f"[{index}/{total}] FAIL '{title}' - no PDF URL"
    base_name = os.path.basename(urlparse(pdf_url).path)
    hash_id = hashlib.md5(pdf_url.encode()).hexdigest()[:8]
    txt_path = output_dir / f"{base_name}_{hash_id}.txt"
    if txt_path.exists():
        return index, True, f"[{index}/{total}] SKIP '{txt_path}' - exists"
    try:
        resp = session.get(pdf_url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        pdf_bytes = resp.content
        if not pdf_bytes.startswith(b"%PDF"):
            raise ValueError(
                "Downloaded file is not a valid PDF (missing %PDF signature)"
            )
        info = pdfinfo_from_bytes(pdf_bytes)
        total_pages = info.get("Pages", 0)
        if total_pages == 0:
            raise ValueError("PDF has no pages")
        text_parts: List[str] = []
        for page in range(1, total_pages + 1):
            img = convert_from_bytes(
                pdf_bytes, dpi=OCR_DPI, first_page=page, last_page=page
            )[0]
            config = f"--oem 1 --psm {OCR_PSM}"
            page_text = pytesseract.image_to_string(img, lang=OCR_LANG, config=config)
            text_parts.append(f"\n--- Page {page} ---\n{page_text}")
        txt_path.write_text(
            f"Title: {title}\nSource PDF: {pdf_url}\n\n{''.join(text_parts)}",
            encoding="utf-8",
        )
        return index, True, ""
    except Exception as e:
        return index, False, f"[{index}/{total}] FAIL '{title}' - {e}"


class ArxivPDFOCR:
    """
    Batch processor for performing OCR on arXiv PDFs.

    Responsibilities:
        - Load paper metadata from a JSON file.
        - Dispatch parallel OCR jobs to worker processes.
        - Manage input and output directories.
        - Log progress and errors.

    Attributes:
        data_dir (Path): Path to the base processed tasks directory.
        input_file (Path): Path to the JSON file containing paper metadata.
        output_dir (Path): Path to the directory where OCR results will be saved.
    """

    def __init__(self):
        """
        Initialize the ArxivPDFOCR processor.

        Sets up paths for the input JSON file and output directory,
        creating the output directory if it does not exist.
        """
        self.data_dir = Path(BASE_DIR) / PROCESSED_TASKS_FOLDER
        self.input_file = self.data_dir / ARXIV_JSON_FILE
        self.output_dir = self.data_dir / PDF_OCR_FOLDER
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_papers(self) -> List[dict]:
        """
        Load paper metadata from the input JSON file.

        Returns:
            List[dict]: A list of paper metadata dictionaries.
        """
        with open(self.input_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def run(self, max_workers: int = 4) -> None:
        """
        Run the OCR process for all papers.

        Steps:
            1. Load paper metadata.
            2. Submit each paper to the process pool for OCR.
            3. Log only errors from workers.
            4. Log progress every 20 completions and at the end.

        Args:
            max_workers (int): Number of parallel worker processes to use.
        """
        papers = self.load_papers()
        total = len(papers)
        logging.info(f"Loaded {total} papers")
        completed = 0
        try:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(
                        process_paper_worker, paper, idx, total, self.output_dir
                    ): idx
                    for idx, paper in enumerate(papers, start=1)
                }
                for future in as_completed(futures):
                    _, success, message = future.result()
                    completed += 1
                    if not success and message:
                        logging.error(message)
                    if completed % 20 == 0 or completed == total:
                        logging.info(f"Progress: {completed}/{total} completed")
            logging.info("OCR processing complete")
        except KeyboardInterrupt:
            logging.warning("Interrupted by user")
            sys.exit(1)


def main():
    """
    Main entry point for the script.

    This function:
        1. Logs the start of the script.
        2. Instantiates the ArxivPDFOCR processor.
        3. Runs the OCR workflow with a number of workers equal to the CPU count (or 4 if unavailable).
        4. Logs successful completion or captures and logs any unhandled exceptions.
        5. Exits with a non-zero status code if an error occurs.

    Intended to be called when the script is executed directly.
    """
    logging.info("Script started")
    try:
        processor = ArxivPDFOCR()
        processor.run(max_workers=os.cpu_count() or 4)
        logging.info("Script finished successfully")
    except Exception as e:
        logging.exception(f"Unhandled error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    """
    Script execution entry point.

    When run as a standalone program, this block calls the main() function
    to start the OCR processing workflow.
    """
    main()
