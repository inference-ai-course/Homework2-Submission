# project_guidelines.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a homework submission repository for Week 2 of a data collection and extraction course. The project focuses on four modules covering web scraping, PDF OCR, automatic speech recognition (ASR), and data cleaning/deduplication.

## Module Structure

The repository is organized into four homework modules under the `homework/` directory:

1. **module1_scraper**: Web scraping arXiv papers with Trafilatura and Tesseract OCR
   - Goal: Scrape 200 papers from arXiv (any subcategory like cs.CL)
   - Extract abstracts using Trafilatura for HTML cleaning
   - Use Tesseract OCR on page screenshots
   - Output: `arxiv_clean.json` with fields: url, title, abstract, authors, date

2. **module2_pdf_ocr**: Batch PDF to text conversion using OCR
   - Goal: Convert arXiv PDFs (same papers as module 1) to text using Tesseract
   - Preserve layout structure (titles, sections) where possible
   - Output: Individual TXT files in `pdf_ocr/` folder

3. **module3_asr**: Automatic speech recognition for YouTube videos
   - Goal: Transcribe 10 short NLP conference talks (~3 minutes each)
   - Use yt-dlp to download YouTube audio
   - Use Tesseract for OCR-based text extraction from transcript images
   - Output: `talks_transcripts.jsonl` with timestamps

4. **module4_cleaning**: End-to-end data cleaning and deduplication
   - Goal: Merge outputs from modules 1-3 into a single cleaned dataset
   - Pipeline: language detection → HTML noise removal → MinHash deduplication (≥0.7 similarity) → PII removal (emails, credit cards, phone numbers) → repetitive n-gram removal
   - Output: `clean_corpus.txt` and `stats.md` with token counts and removal percentages

## Development Environment

### Python Environment
- Uses a virtual environment (`venv/`) with Python 3.11
- Key dependencies installed:
  - `pytesseract` for OCR
  - `pillow` for image processing
  - `huggingface-hub` and `torch` for ML models
  - Standard data science libraries (numpy, etc.)

### Installing System Dependencies
Before running the code, ensure Tesseract OCR is installed:
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt install tesseract-ocr`
- Windows: Download from [Tesseract GitHub releases](https://github.com/tesseract-ocr/tesseract/releases)

### Running Code
- Activate virtual environment: `source venv/bin/activate` (Unix/macOS) or `venv\Scripts\activate` (Windows)
- Run Jupyter notebooks: `jupyter notebook "Class 2 Homework.ipynb"`
- Each module's scripts should be run from within their respective directories

## Key Libraries and Tools

### Core Technologies
- **Trafilatura**: HTML content extraction and cleaning
- **Tesseract OCR**: Optical character recognition (use `pytesseract` Python wrapper)
  - Use `--psm` flag to control page segmentation mode (e.g., `--psm 6` for uniform text blocks)
- **yt-dlp**: YouTube audio/video downloading
- **pdf2image**: Convert PDF pages to images for OCR processing
- **datasketch**: MinHash LSH for document deduplication
- **langdetect**: Language detection for filtering

### Data Cleaning Pipeline
- Language detection filters out non-English content
- MinHash with similarity threshold ≥ 0.7 for near-duplicate detection
- PII patterns to remove: emails, credit card numbers, phone numbers
- N-gram repetition detection and removal

## File Size Constraints
- Output file `arxiv_clean.json` must be ≤ 1MB
- Consider pagination or sampling if scraping results in larger files
