#!/usr/bin/env python3
"""
pdf_ocr.py
Module 2: Batch PDF to Text OCR
Converts PDF files to text using Tesseract OCR.
Christine Zhao
2025-11-02
"""

import os
import json
import requests
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from typing import List
import time


class PDFOCRConverter:
    """Converts PDF files to text using OCR."""

    def __init__(self, papers_json: str = "../module1_scraper/arxiv_clean.json",
                 output_dir: str = "pdf_ocr"):
        """
        Initialize the PDF OCR converter.

        Args:
            papers_json: Path to the JSON file with paper information
            output_dir: Directory to save OCR text files
        """
        self.papers_json = papers_json
        self.output_dir = output_dir
        self.papers = []

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def load_papers(self):
        """Load papers from JSON file."""
        try:
            with open(self.papers_json, 'r', encoding='utf-8') as f:
                self.papers = json.load(f)
            print(f"Loaded {len(self.papers)} papers from {self.papers_json}")
        except FileNotFoundError:
            print(f"Error: {self.papers_json} not found. Run module1 first.")
            self.papers = []

    def download_pdf(self, arxiv_id: str, output_path: str) -> bool:
        """
        Download PDF from arXiv.

        Args:
            arxiv_id: arXiv paper ID
            output_path: Path to save the PDF

        Returns:
            True if successful, False otherwise
        """
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        try:
            print(f"Downloading PDF: {pdf_url}")
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                f.write(response.content)

            return True

        except Exception as e:
            print(f"Error downloading PDF {arxiv_id}: {e}")
            return False

    def pdf_to_text_ocr(self, pdf_path: str, max_pages: int = 5) -> str:
        """
        Convert PDF to text using OCR.

        Args:
            pdf_path: Path to the PDF file
            max_pages: Maximum number of pages to process (to save time)

        Returns:
            Extracted text
        """
        try:
            print(f"Converting PDF to images: {pdf_path}")

            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=max_pages)

            print(f"Processing {len(images)} pages with OCR...")
            extracted_text = []

            for i, image in enumerate(images, 1):
                print(f"  Processing page {i}/{len(images)}")

                # Perform OCR with layout preservation
                text = pytesseract.image_to_string(
                    image,
                    config='--psm 6'  # Assume uniform block of text
                )

                extracted_text.append(f"\n--- Page {i} ---\n{text}")

            return "\n".join(extracted_text)

        except Exception as e:
            print(f"Error during OCR: {e}")
            return ""

    def process_papers(self, max_papers: int = 10):
        """
        Process papers and convert to text.

        Args:
            max_papers: Maximum number of papers to process
        """
        self.load_papers()

        if not self.papers:
            print("No papers to process.")
            return

        # Process only first N papers to save time
        papers_to_process = self.papers[:max_papers]

        print(f"\nProcessing {len(papers_to_process)} papers...")

        for i, paper in enumerate(papers_to_process, 1):
            arxiv_id = paper.get('arxiv_id', '')
            title = paper.get('title', 'Unknown')

            print(f"\n{'='*60}")
            print(f"Paper {i}/{len(papers_to_process)}: {title}")
            print(f"arXiv ID: {arxiv_id}")
            print('='*60)

            # Download PDF
            pdf_path = f"temp_{arxiv_id}.pdf"
            if not self.download_pdf(arxiv_id, pdf_path):
                continue

            # Convert to text
            text = self.pdf_to_text_ocr(pdf_path, max_pages=3)

            # Save text
            output_filename = os.path.join(self.output_dir, f"{arxiv_id}.txt")
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n")
                f.write(f"arXiv ID: {arxiv_id}\n")
                f.write(f"URL: {paper.get('url', '')}\n")
                f.write("\n" + "="*60 + "\n\n")
                f.write(text)

            print(f"Saved to: {output_filename}")

            # Clean up temporary PDF
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

            # Be polite
            time.sleep(2)

        print(f"\n{'='*60}")
        print(f"OCR processing completed!")
        print(f"Output saved to: {self.output_dir}/")
        print('='*60)


def main():
    """Main function to run PDF OCR."""
    converter = PDFOCRConverter()

    # Process up to 10 papers (can be increased)
    converter.process_papers(max_papers=10)


if __name__ == "__main__":
    main()
