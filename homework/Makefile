.PHONY: help install test clean run module1 module2 module3 module4

help:
	@echo "Homework 2 - Data Collection & Extraction"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make test       - Test setup and dependencies"
	@echo "  make run        - Run all modules sequentially"
	@echo "  make module1    - Run Module 1 (arXiv scraper)"
	@echo "  make module2    - Run Module 2 (PDF OCR)"
	@echo "  make module3    - Run Module 3 (YouTube ASR)"
	@echo "  make module4    - Run Module 4 (Data cleaning)"
	@echo "  make clean      - Remove all generated output files"
	@echo ""

install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo ""
	@echo "Note: Please install system dependencies manually:"
	@echo "  macOS: brew install tesseract poppler"
	@echo "  Linux: sudo apt install tesseract-ocr poppler-utils"

test:
	@echo "Testing setup..."
	python test_setup.py

run:
	@echo "Running all modules..."
	python run_all.py

module1:
	@echo "Running Module 1: arXiv Scraper"
	cd module1_scraper && python arxiv_scraper.py

module2:
	@echo "Running Module 2: PDF OCR"
	cd module2_pdf_ocr && python pdf_ocr.py

module3:
	@echo "Running Module 3: YouTube ASR"
	cd module3_asr && python youtube_transcriber.py

module4:
	@echo "Running Module 4: Data Cleaning"
	cd module4_cleaning && python data_cleaner.py

clean:
	@echo "Cleaning generated output files..."
	rm -f module1_scraper/*.json
	rm -rf module2_pdf_ocr/pdf_ocr/
	rm -f module2_pdf_ocr/*.pdf
	rm -f module3_asr/*.jsonl
	rm -f module3_asr/*.mp3
	rm -f module4_cleaning/clean_corpus.txt
	rm -f module4_cleaning/stats.md
	@echo "Cleaned!"
