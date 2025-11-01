# Quick Start Guide

## Installation (5 minutes)

### 1. System Dependencies

```bash
# macOS
brew install tesseract poppler

# Ubuntu/Debian
sudo apt update
sudo apt install tesseract-ocr poppler-utils
```

### 2. Python Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install all packages
pip install -r requirements.txt
```

### 3. Verify Setup

```bash
python test_setup.py
```

If all tests pass, you're ready to go!

## Running the Project

### Quick Run (All Modules)

```bash
python run_all.py
```

This will execute all four modules sequentially and generate all outputs.

### Run Individual Modules

```bash
# Module 1: Scrape arXiv papers
cd homework/module1_scraper && python arxiv_scraper.py

# Module 2: Convert PDFs to text
cd homework/module2_pdf_ocr && python pdf_ocr.py

# Module 3: Transcribe YouTube videos
cd homework/module3_asr && python youtube_transcriber.py

# Module 4: Clean and deduplicate
cd homework/module4_cleaning && python data_cleaner.py
```

## Expected Runtime

- **Module 1**: ~5-10 minutes (200 papers)
- **Module 2**: ~20-50 minutes (10 PDFs, 3 pages each)
- **Module 3**: ~10-20 minutes (depends on video length)
- **Module 4**: ~2-5 minutes

**Total**: ~45-90 minutes

## Output Files

After completion, check these locations:

```
homework/
├── module1_scraper/
│   └── arxiv_clean.json          # Scraped papers (≤1MB)
├── module2_pdf_ocr/
│   └── pdf_ocr/
│       ├── 2301.12345.txt        # OCR text files
│       ├── 2301.12346.txt
│       └── ...
├── module3_asr/
│   └── talks_transcripts.jsonl   # Video transcripts
└── module4_cleaning/
    ├── clean_corpus.txt          # Cleaned corpus
    └── stats.md                  # Cleaning statistics
```

## Customization Tips

### Change arXiv Category

Edit `homework/module1_scraper/arxiv_scraper.py`:

```python
scraper = ArxivScraper(category="cs.AI", max_papers=200)
```

Popular categories:
- `cs.CL` - Computation and Language (NLP)
- `cs.AI` - Artificial Intelligence
- `cs.LG` - Machine Learning
- `cs.CV` - Computer Vision

### Adjust Number of PDFs

Edit `homework/module2_pdf_ocr/pdf_ocr.py`:

```python
converter.process_papers(max_papers=20)  # Default is 10
```

### Use Different Whisper Model

Edit `homework/module3_asr/youtube_transcriber.py`:

```python
transcriber.load_whisper_model(model_size="tiny")  # Options: tiny, base, small, medium, large
```

| Model  | Speed   | Accuracy | RAM  |
|--------|---------|----------|------|
| tiny   | Fastest | Lower    | 1GB  |
| base   | Fast    | Good     | 1GB  |
| small  | Medium  | Better   | 2GB  |
| medium | Slow    | Great    | 5GB  |
| large  | Slowest | Best     | 10GB |

## Troubleshooting

### Error: "Tesseract not found"

```bash
# macOS
brew install tesseract

# Add to PATH if needed
export PATH="/usr/local/bin:$PATH"
```

### Error: "Unable to load pdf document"

Install Poppler:

```bash
# macOS
brew install poppler

# Ubuntu
sudo apt install poppler-utils
```

### Error: "yt-dlp command not found"

```bash
pip install yt-dlp
```

### Whisper Model Download is Slow

Models are downloaded on first use:
- Tiny: ~75 MB
- Base: ~145 MB
- Small: ~488 MB

Be patient on the first run!

### Out of Memory (Module 3)

Use a smaller Whisper model:

```python
transcriber.load_whisper_model(model_size="tiny")
```

## Need Help?

1. Check the full README.md for detailed documentation
2. Verify all dependencies: `python test_setup.py`
3. Review error messages carefully
4. Ensure you have a stable internet connection

## Next Steps

After running all modules:

1. Check `homework/module4_cleaning/stats.md` for cleaning statistics
2. Review `clean_corpus.txt` for the final output
3. Analyze `arxiv_clean.json` to see scraped paper data
4. Explore the OCR text files in `pdf_ocr/` directory

Happy coding!
