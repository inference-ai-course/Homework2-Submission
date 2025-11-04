# Week 2 Homework: arXiv Paper Scraper & LLM Alignment Concepts

## Overview

This homework builds on concepts from the **Class 2 Lecture: From Transformers to Alignment**. You will:

- Scrape recent arXiv papers in a chosen category (e.g., `cs.CL`)
- Clean HTML content using Trafilatura
- (Bonus) Extract abstract text from screenshots using Tesseract OCR
- Perform batch OCR on images and PDFs
- Transcribe audio from YouTube talks using Whisper ASR
- Clean, deduplicate, and merge all outputs into a final corpus
- Save results as JSON and text files for further analysis

## Project Structure

```
homework/
├── homework.ipynb                   # Main notebook orchestrating all tasks
├── ocr_batch_code.py                # Batch image OCR processor
├── arxiv_abstract_scraper.py        # arXiv abstract scraping & HTML cleaning
├── arxiv_pdf_ocr.py                 # Batch PDF OCR for arXiv papers
├── whisper_ocr_bot.py               # ASR + OCR for YouTube talks
├── data_cleaner.py                  # End-to-end data cleaning & deduplication
├── README.md                        # Project documentation
├── 01_ingest/                       # Input folder for raw files
│   ├── images/                      # Image OCR bulk input: Images for OCR
│   └── youtube_links.txt            # Automatic Speech Recognition (ASR) input: Audio files for ASR
├── 02_processed_tasks/              # Output folder for results
│   ├── pdf_ocr/                     # PDF to Text OCR bulk output: OCR'd text files from PDFs
│   ├── arxiv_clean.json             # Web Scraping & HTML Cleaning output: Scraped arXiv metadata
│   └── talks_transcripts.jsonl      # Automatic Speech Recognition (ASR) output: Whisper transcripts
└── 03_processed_tasks/              # Output folder for task 4 results
    ├── ocr_output/                  # Image OCR bulk output: Image text files
    ├── clean_corpus.txt             # Data Cleaning & Deduplication output: Final cleaned corpus
    └── stats.md                     # Data Cleaning & Deduplication output: Cleaning statistics

```

## Workflow Overview

1. **Image OCR**

   - Preprocess images (grayscale, brightness/contrast, denoise)
   - Run batch OCR using `ocr_batch.py`

2. **Web Scraping & HTML Cleaning**

   - Scrape arXiv abstracts with `arxiv_abstract_scraper.py`
   - Clean HTML, OCR screenshots, save to `02_processed_tasks/arxiv_clean.json`

3. **PDF to Text OCR**

   - Download arXiv PDFs, convert to images
   - OCR with `arxiv_pdf_ocr.py`, save results in `02_processed_tasks/pdf_ocr/`

4. **Automatic Speech Recognition (ASR)**

   - Download audio with yt-dlp
   - Transcribe with Whisper using `whisper_ocr_bot.py`
   - OCR images in transcripts, save to `02_processed_tasks/talks_transcripts.jsonl`

5. **Data Cleaning & Deduplication**
   - Merge outputs, clean and deduplicate with `data_cleaner.py`
   - Save final corpus and statistics

---

## Usage

Run each section in `homework.ipynb` sequentially. Each script can also be run independently for its respective task.

## Requirements

- Python 3.8+
- `tesseract-ocr`, `trafilatura`, `pdf2image`, `yt-dlp`, `openai-whisper`, `datasketch`, `langdetect`, `bs4`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Output

- `02_processed_tasks/pdf_ocr/` — OCR'd text files from PDFs
- `02_processed_tasks/arxiv_clean.json` — Scraped arXiv metadata
- `02_processed_tasks/talks_transcripts.jsonl` — Whisper transcripts
- `03_clean_corpus/ocr_output/` — Image text files
- `03_clean_corpus/clean_corpus.txt` — Final cleaned and deduplicated corpus
- `03_clean_corpus/stats.md` — Cleaning statistics

---

**Author:** Carlos  
**Course:** MLE in Gen AI  
**Date:** 2025-09-05
