# Quick Reference Card

## Installation (One-time Setup)

```bash
# System dependencies (macOS)
brew install tesseract poppler

# System dependencies (Ubuntu/Linux)
sudo apt install tesseract-ocr poppler-utils

# Python dependencies
pip install -r requirements.txt

# Verify setup
python test_setup.py
```

## Running the Project

### All Modules at Once
```bash
python run_all.py
# OR
make run
```

### Individual Modules
```bash
# Module 1: arXiv Scraper
cd homework/module1_scraper && python arxiv_scraper.py
# OR: make module1

# Module 2: PDF OCR
cd homework/module2_pdf_ocr && python pdf_ocr.py
# OR: make module2

# Module 3: YouTube ASR
cd homework/module3_asr && python youtube_transcriber.py
# OR: make module3

# Module 4: Data Cleaning
cd homework/module4_cleaning && python data_cleaner.py
# OR: make module4
```

## Output Files

| Module | Output File(s) | Location |
|--------|---------------|----------|
| 1 | arxiv_clean.json | homework/module1_scraper/ |
| 2 | *.txt files | homework/module2_pdf_ocr/pdf_ocr/ |
| 3 | talks_transcripts.jsonl | homework/module3_asr/ |
| 4 | clean_corpus.txt, stats.md | homework/module4_cleaning/ |

## Common Customizations

### Change arXiv Category
Edit `homework/module1_scraper/arxiv_scraper.py`, line ~185:
```python
scraper = ArxivScraper(category="cs.AI", max_papers=200)
```

### Process More PDFs
Edit `homework/module2_pdf_ocr/pdf_ocr.py`, line ~171:
```python
converter.process_papers(max_papers=20)  # Default: 10
```

### Change Whisper Model
Edit `homework/module3_asr/youtube_transcriber.py`, line ~26:
```python
self.load_whisper_model(model_size="small")  # Options: tiny, base, small, medium, large
```

### Adjust Deduplication
Edit `homework/module4_cleaning/data_cleaner.py`, line ~333:
```python
cleaner = DataCleaner(similarity_threshold=0.8)  # Default: 0.7
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| Tesseract not found | `brew install tesseract` or `apt install tesseract-ocr` |
| pdf2image error | `brew install poppler` or `apt install poppler-utils` |
| yt-dlp not found | `pip install yt-dlp` |
| Out of memory (Whisper) | Use smaller model: `model_size="tiny"` |
| Import errors | `pip install -r requirements.txt` |

## Makefile Commands

```bash
make help       # Show all available commands
make install    # Install Python dependencies
make test       # Test setup
make run        # Run all modules
make module1    # Run Module 1 only
make module2    # Run Module 2 only
make module3    # Run Module 3 only
make module4    # Run Module 4 only
make clean      # Remove all output files
```

## File Locations

```
homework/
├── module1_scraper/
│   └── arxiv_scraper.py          ← Edit to change category
├── module2_pdf_ocr/
│   └── pdf_ocr.py                ← Edit to change PDF count
├── module3_asr/
│   ├── youtube_transcriber.py    ← Edit to change model
│   └── video_config.json         ← Add/remove videos
└── module4_cleaning/
    └── data_cleaner.py           ← Edit cleaning parameters
```

## Estimated Runtimes

| Module | Time |
|--------|------|
| Module 1 | 5-10 min |
| Module 2 | 20-50 min |
| Module 3 | 10-20 min |
| Module 4 | 2-5 min |
| **Total** | **45-90 min** |

## Key File Descriptions

- `run_all.py` - Runs all modules sequentially
- `test_setup.py` - Validates dependencies
- `requirements.txt` - Python package list
- `Makefile` - Convenience commands
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick start guide
- `CLAUDE.md` - AI assistant guidance
- `PROJECT_SUMMARY.md` - Technical overview

## Need More Help?

1. Read `QUICKSTART.md` for detailed quick start
2. Read `README.md` for comprehensive documentation
3. Run `python test_setup.py` to check dependencies
4. Run `make help` to see all available commands
