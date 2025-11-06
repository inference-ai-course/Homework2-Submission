# 📚 AI Research Data Collection & Processing Toolkit

A comprehensive Python toolkit for collecting, processing, and analyzing research data from arXiv, PDFs, and audio sources. Perfect for researchers, students, and AI enthusiasts working with academic papers and multimedia content!

## 🌟 Features Overview

This toolkit provides four main workflows:

1. **📄 arXiv Paper Collection** - Search, scrape, and download research papers
2. **🔍 PDF Text Extraction** - Convert PDFs to searchable text using OCR
3. **🎙️ Audio Transcription** - Transcribe YouTube videos and audio files
4. **✨ Advanced Web Scraping** - Clean HTML content with Trafilatura

---

## 🚀 Quick Start

### Installation

```bash
# Install required packages
pip install -r requirements.txt

# Install system dependencies
# For Tesseract OCR:
# - macOS: brew install tesseract
# - Ubuntu: sudo apt install tesseract-ocr
# - Windows: Download from https://github.com/tesseract-ocr/tesseract

# For yt-dlp (YouTube downloader):
pip install yt-dlp
```

---

## 📖 Task Guides

### Task 1: arXiv Paper Collection Pipeline

**What it does:** Searches arXiv, scrapes paper metadata, downloads PDFs, and extracts text using OCR.

**Notebook:** `src/task1.ipynb`

**Key Features:**
- 🔎 Custom arXiv search queries
- 🕷️ Background scraping with threading
- 📥 Automatic PDF downloads
- 📝 Batch OCR processing

**Example Usage:**

```python
from utils.arxiv_search import build_arxiv_search_url, run_scraper_in_background
from utils.arxiv_search import scrape_arxiv_details_from_json_threaded
from utils.pdf_ocr_extractor import batch_process_pdfs

# 1. Build search URL
arxiv_url = build_arxiv_search_url(size=20, query="Artificial Intelligence")

# 2. Scrape search results
run_scraper_in_background(url=arxiv_url, output_file="data/scraped/papers.json")

# 3. Get detailed metadata (threaded for speed!)
details = scrape_arxiv_details_from_json_threaded("data/scraped/papers.json", max_workers=4)

# 4. Download PDFs and extract text
get_pdf_arxiv(cleaned_json="data/cleaned/arxiv_clean.json", save_dir="data/pdfs")
batch_process_pdfs(pdf_files, output_text_files, "data/pdf_img")
```

**Output:**
- `data/scraped/` - Raw search results (JSON)
- `data/cleaned/` - Enriched metadata (JSON)
- `data/pdfs/` - Downloaded PDF files
- `data/pdf_img/` - Intermediate images from PDFs
- `*.txt` files - Extracted text from PDFs

---

### Task 1 Bonus: Advanced Scraping with Trafilatura

**What it does:** Uses Trafilatura for cleaner HTML extraction and processes multiple topics in parallel.

**Notebook:** `src/task1_bonus.ipynb`

**Key Features:**
- 🧹 Cleaner text extraction with Trafilatura
- 🚀 Multi-threaded processing (5 workers)
- 📊 Processes multiple research topics simultaneously

**Example Usage:**

```python
from utils.trafilatura_processor import process_arxiv_url_with_trafilatura

# Process a single URL with clean extraction
result = process_arxiv_url_with_trafilatura("https://arxiv.org/abs/2301.12345")
# Returns: {url, title, abstract, authors, date}
```

---

### Task 2: PDF Text Extraction

**What it does:** Converts PDF files to text using Tesseract OCR.

**Notebook:** `src/task2.ipynb`

**Key Features:**
- 📄 Batch PDF processing
- 🖼️ PDF to image conversion
- 🔤 OCR text extraction
- 📝 Automatic text file generation

**Example Usage:**

```python
from utils.pdf_ocr_extractor import extract_text_from_pdf

# Extract text from a single PDF
text = extract_text_from_pdf("paper.pdf", dpi=300, lang="eng")

# Process multiple PDFs
from utils.pdf_ocr_extractor import batch_process_pdfs
results = batch_process_pdfs(pdf_files, output_text_files, "pdf_images")
```

---

### Task 3: Audio Transcription with Whisper

**What it does:** Downloads YouTube audio and transcribes it using OpenAI's Whisper model with multi-threading for speed.

**Notebook:** `src/task3.ipynb`

**Key Features:**
- 🎵 YouTube playlist/video download
- 🎙️ Multi-threaded transcription (3x faster!)
- 💾 Auto-saves transcripts as .txt files
- 📊 Generates summary JSONL file

**Example Usage:**

```python
from utils.yt_downloader import download_youtube_audio_v2
from utils.transcriber import transcribe_folder_threaded

# 1. Download YouTube playlist
playlist_url = "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
download_youtube_audio_v2(playlist_url, "data/audio/downloads", is_playlist=True)

# 2. Transcribe all files with threading (fast!)
results = transcribe_folder_threaded(
    folder_path="data/audio/downloads",
    model_name="tiny",  # Options: tiny, base, small, medium, large
    max_workers=3  # Adjust based on your CPU
)

# Each audio file gets a .txt transcript saved next to it
# Plus a transcription_summary.jsonl with all results
```

**Output:**
- `*.mp3` - Downloaded audio files
- `*.txt` - Transcription for each audio file
- `transcription_summary.jsonl` - Complete summary

---

## 🛠️ Utility Modules (`src/utils/`)

### `arxiv_search.py`
**Purpose:** arXiv search, scraping, and PDF downloads

**Key Functions:**
- `build_arxiv_search_url()` - Create custom search URLs
- `scrape_arxiv_url_to_json()` - Scrape search results
- `run_scraper_in_background()` - Non-blocking scraping
- `scrape_arxiv_details_from_json_threaded()` - Fast metadata extraction
- `download_pdf()` - Download single PDF by arXiv ID
- `get_pdf_arxiv()` - Batch PDF downloads

### `pdf_ocr_extractor.py`
**Purpose:** PDF to text conversion using Tesseract OCR

**Key Functions:**
- `extract_text_from_pdf()` - Single PDF extraction
- `batch_process_pdfs()` - Process multiple PDFs
- `convert_pdf_to_images()` - PDF → images
- `run_tesseract_on_images()` - Images → text

### `yt_downloader.py`
**Purpose:** YouTube audio downloading

**Key Functions:**
- `download_youtube_audio()` - Download single video
- `download_youtube_audio_v2()` - Download video or playlist

### `transcriber.py`
**Purpose:** Audio transcription with Whisper

**Key Functions:**
- `transcribe_audio()` - Transcribe single file
- `transcribe_single_file()` - Transcribe with metadata
- `transcribe_folder_threaded()` - **Fast batch transcription with threading!**

### `trafilatura_processor.py`
**Purpose:** Clean HTML extraction

**Key Functions:**
- `process_arxiv_url_with_trafilatura()` - Extract clean text from arXiv pages

### `screenshot_taker.py`
**Purpose:** Web page screenshots using Selenium

**Key Functions:**
- `take_screenshot()` - Capture webpage as image

---

## 📦 Libraries Used

### Core Dependencies
- **requests** - HTTP requests for web scraping
- **beautifulsoup4** - HTML parsing
- **trafilatura** - Clean text extraction from HTML
- **pytesseract** - Python wrapper for Tesseract OCR
- **pdf2image** - Convert PDF pages to images
- **Pillow (PIL)** - Image processing
- **openai-whisper** - Audio transcription
- **yt-dlp** - YouTube video/audio downloading
- **selenium** - Web browser automation
- **webdriver-manager** - Automatic WebDriver management
- **datasketch** - MinHash for deduplication (bonus task)
- **langdetect** - Language detection (bonus task)

### System Requirements
- **Tesseract OCR** - Must be installed separately
- **FFmpeg** - Required for audio processing (auto-installed with yt-dlp)
- **Chrome/Chromium** - For screenshot functionality

---

## 📁 Project Structure

```
.
├── src/
│   ├── task1.ipynb          # arXiv collection pipeline
│   ├── task1_bonus.ipynb    # Advanced scraping with Trafilatura
│   ├── task2.ipynb          # PDF text extraction
│   ├── task3.ipynb          # Audio transcription
│   └── utils/
│       ├── arxiv_search.py       # arXiv utilities
│       ├── pdf_ocr_extractor.py  # PDF/OCR utilities
│       ├── yt_downloader.py      # YouTube downloader
│       ├── transcriber.py        # Audio transcription
│       ├── trafilatura_processor.py  # HTML cleaning
│       └── screenshot_taker.py   # Screenshot utility
├── data/                    # Output directory
│   ├── scraped/            # Raw scraped data
│   ├── cleaned/            # Processed metadata
│   ├── pdfs/               # Downloaded PDFs
│   ├── pdf_img/            # PDF images
│   ├── pdf_ocr/            # Extracted text
│   └── audio/              # Audio files & transcripts
├── README.md
└── requirements.txt
```

---

## 💡 Tips & Best Practices

### For arXiv Scraping:
- ⏱️ Use `time.sleep()` between requests to be respectful to arXiv servers
- 🧵 Use threaded functions for faster processing
- 📊 Start with small page sizes (20-50) for testing

### For PDF OCR:
- 🖼️ Higher DPI (300+) = better accuracy but slower processing
- 🌍 Specify correct language with `lang` parameter
- 💾 Keep intermediate images for debugging

### For Audio Transcription:
- 🎯 Use "tiny" model for speed, "large" for accuracy
- 🚀 Adjust `max_workers` based on your CPU cores
- 💾 Transcripts auto-save next to audio files

---

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements!

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- arXiv for providing open access to research papers
- OpenAI for the Whisper model
- The open-source community for all the amazing libraries!

---

**Happy researching! 🎓✨**
