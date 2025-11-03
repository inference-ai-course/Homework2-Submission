# Week 2 Homework: Data Collection & Extraction

This repository contains implementations for all four modules of the Week 2 homework assignment, focusing on data collection, OCR, ASR, and data cleaning.

## Project Structure

```
Homework2-Submission/homework/
├── module1_scraper/       # arXiv paper scraper
│   └── arxiv_scraper.py
├── module2_pdf_ocr/       # PDF to text OCR
│   └── pdf_ocr.py
├── module3_asr/           # YouTube ASR transcription
│   └── youtube_transcriber.py
├── module4_cleaning/      # Data cleaning pipeline
│   └── data_cleaner.py
├── requirements.txt
├── run_all.py             # Main runner script
└── README.md
```

## Setup Instructions

### 1. Install System Dependencies

**Tesseract OCR** (required for modules 1 and 2):
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt update
sudo apt install tesseract-ocr

# Windows
# Download from: https://github.com/tesseract-ocr/tesseract/releases
```

**Poppler** (required for PDF to image conversion):
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt install poppler-utils

# Windows
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
```

### 2. Install Python Dependencies

```bash
# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Install yt-dlp (for Module 3)

```bash
# Using pip
pip install yt-dlp

# Or using your package manager
brew install yt-dlp  # macOS
```

## Running the Modules

### Option 1: Run All Modules Sequentially

```bash
python run_all.py
```

This will execute all four modules in order and generate all required outputs.

### Option 2: Run Individual Modules

#### Module 1: arXiv Paper Scraper

```bash
cd module1_scraper
python arxiv_scraper.py
```

**Output**: `arxiv_clean.json` (containing 200 arXiv papers with abstracts)

**Features**:
- Scrapes latest papers from arXiv (default category: cs.CL)
- Uses Trafilatura for HTML content extraction
- Extracts title, abstract, authors, and date
- Saves structured JSON output

#### Module 2: PDF to Text OCR

```bash
cd module2_pdf_ocr
python pdf_ocr.py
```

**Output**: `pdf_ocr/` directory with individual `.txt` files

**Features**:
- Downloads PDFs from arXiv
- Converts PDF pages to images (300 DPI)
- Uses Tesseract OCR for text extraction
- Preserves document layout

**Note**: Processes first 10 papers by default (can be increased in code)

#### Module 3: YouTube ASR Transcription

```bash
cd module3_asr
python youtube_transcriber.py
```

**Output**: `talks_transcripts.jsonl`

**Features**:
- Downloads audio from YouTube videos using yt-dlp
- Transcribes using OpenAI Whisper
- Includes timestamps for each segment
- Saves as JSONL format

**Note**: Update the `video_list` in the script with actual NLP conference talk URLs

#### Module 4: Data Cleaning Pipeline

```bash
cd module4_cleaning
python data_cleaner.py
```

**Outputs**:
- `clean_corpus.txt` - Cleaned and deduplicated corpus
- `stats.md` - Detailed statistics about the cleaning process

**Features**:
- Merges data from all three previous modules
- Language detection and filtering (English only)
- HTML noise removal
- MinHash-based deduplication (similarity ≥ 0.7)
- PII removal (emails, phone numbers, credit cards)
- Repetitive n-gram filtering
- Comprehensive statistics generation

## Module Details

### Module 1: Web Scraping & HTML Cleaning

**Objective**: Scrape 200 papers from arXiv and extract clean abstracts

**Technologies**:
- `requests` for HTTP requests
- `BeautifulSoup` for HTML parsing
- `trafilatura` for content extraction

**Output Schema**:
```json
{
  "url": "https://arxiv.org/abs/...",
  "arxiv_id": "2301.12345",
  "title": "Paper Title",
  "abstract": "Paper abstract text...",
  "authors": ["Author 1", "Author 2"],
  "date": "Submission date"
}
```

### Module 2: PDF to Text OCR

**Objective**: Convert arXiv PDFs to searchable text

**Technologies**:
- `pdf2image` for PDF to image conversion
- `pytesseract` for OCR
- `Pillow` for image processing

**Key Parameters**:
- DPI: 300 (high quality)
- PSM mode: 6 (uniform text blocks)
- Max pages: 3 per document (for efficiency)

### Module 3: Automatic Speech Recognition

**Objective**: Transcribe NLP conference talks from YouTube

**Technologies**:
- `yt-dlp` for video/audio download
- `whisper` (OpenAI) for transcription

**Model**: Base model (good balance of speed and accuracy)

**Output Format**:
```json
{
  "url": "https://youtube.com/...",
  "title": "Video title",
  "full_text": "Complete transcription...",
  "segments": [
    {"start": 0.0, "end": 5.2, "text": "Segment text"}
  ]
}
```

### Module 4: Data Cleaning & Deduplication

**Objective**: Create a clean, deduplicated corpus from all sources

**Pipeline Steps**:
1. **Language Detection**: Keep only English documents
2. **HTML Cleaning**: Remove tags and special characters
3. **Deduplication**: MinHash LSH with 70% similarity threshold
4. **PII Removal**: Redact emails, phone numbers, credit cards
5. **N-gram Filtering**: Remove documents with excessive repetition

**Statistics Tracked**:
- Document counts at each stage
- Token counts before/after
- Removal percentages

## Expected Outputs

After running all modules, you should have:

1. `module1_scraper/arxiv_clean.json` (≤ 1MB)
2. `module2_pdf_ocr/pdf_ocr/*.txt` (multiple files)
3. `module3_asr/talks_transcripts.jsonl`
4. `module4_cleaning/clean_corpus.txt`
5. `module4_cleaning/stats.md`

## Customization

### Changing arXiv Category

Edit `module1_scraper/arxiv_scraper.py`:
```python
scraper = ArxivScraper(category="cs.AI", max_papers=200)  # Change category
```

### Processing More PDFs

Edit `module2_pdf_ocr/pdf_ocr.py`:
```python
converter.process_papers(max_papers=50)  # Increase from default 10
```

### Adding YouTube Videos

Edit `module3_asr/youtube_transcriber.py`:
```python
video_list = [
    {"url": "https://www.youtube.com/...", "title": "Talk Title", "duration": "180"},
    # Add more videos
]
```

### Adjusting Deduplication Threshold

Edit `module4_cleaning/data_cleaner.py`:
```python
cleaner = DataCleaner(similarity_threshold=0.8)  # Stricter deduplication
```

## Troubleshooting

### Tesseract Not Found
```bash
# Add Tesseract to PATH or set in code:
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
```

### PDF Conversion Errors
Ensure Poppler is installed and in your PATH.

### YouTube Download Fails
- Check video availability and region restrictions
- Update yt-dlp: `pip install -U yt-dlp`

### Memory Issues with Whisper
Use a smaller model:
```python
transcriber.load_whisper_model(model_size="tiny")  # Faster, less accurate
```

## Performance Notes

- **Module 1**: ~5-10 minutes for 200 papers
- **Module 2**: ~2-5 minutes per PDF (depends on page count)
- **Module 3**: ~1-2 minutes per video (for 3-minute talks)
- **Module 4**: ~2-5 minutes (depends on corpus size)

## Requirements

- Python 3.8+
- 8GB RAM minimum (16GB recommended for Module 3)
- Internet connection for downloading papers and videos
- ~2GB free disk space

## License

MIT License - see LICENSE file for details

## Author

Christine Zhao - Homework 2 Submission
