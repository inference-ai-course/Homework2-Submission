"""
data_cleaner.py

An end-to-end text data cleaning pipeline for multi-source corpora.

This script ingests raw text data from multiple formats (plain text, JSON, JSONL),
applies a series of configurable cleaning steps, and outputs a deduplicated,
language-filtered, PII-sanitized corpus along with cleaning statistics.

The pipeline includes:
    - Loading text from OCR-processed PDFs, arXiv JSON exports, and talks transcripts.
    - Language filtering (default: English only).
    - HTML tag stripping.
    - Near-duplicate detection and removal using MinHash LSH.
    - Personally Identifiable Information (PII) masking (emails, credit cards, phone numbers).
    - Removal of excessively repeated n-grams.
    - Output of cleaned corpus and a Markdown stats report.

Environment variables (via `.env`) control:
    - Input/output directories
    - MinHash similarity threshold
    - N-gram size and repetition limits
    - Logging verbosity

Typical usage:
    $ python data_cleaner.py

Dependencies:
    - beautifulsoup4
    - datasketch
    - python-dotenv
    - langdetect

Author:
    Carlos (2025)
"""

import json
import logging
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import List, Union

from bs4 import BeautifulSoup
from datasketch import MinHash, MinHashLSH
from dotenv import load_dotenv
from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)

PROCESSED_TASKS_FOLDER = os.getenv("PROCESSED_TASKS_FOLDER", "02_processed_tasks")
CLEAN_CORPUS_FOLDER = os.getenv("CLEAN_CORPUS_FOLDER", "03_clean_corpus")
PDF_OCR_FOLDER = os.getenv("PDF_OCR_FOLDER", "pdf_ocr")
ARXIV_JSON_FILE = os.getenv("ARXIV_JSON_FILE", "arxiv_clean.json")
TALKS_JSONL_FILE = os.getenv("TALKS_JSONL_FILE", "talks_transcripts.jsonl")
MINHASH_THRESHOLD = float(os.getenv("MINHASH_THRESHOLD", "0.7"))
NGRAM_SIZE = int(os.getenv("NGRAM_SIZE", "3"))
MAX_NGRAM_REPEATS = int(os.getenv("MAX_NGRAM_REPEATS", "3"))

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / PROCESSED_TASKS_FOLDER
OUTPUT_PATH = BASE_DIR / CLEAN_CORPUS_FOLDER


class EndToEndCleaner:
    """
    End-to-end text cleaning pipeline.

    This class orchestrates the loading, cleaning, deduplication, and saving
    of text documents from multiple sources. It is designed for large-scale
    corpus preparation where heterogeneous formats and noisy data are common.

    Attributes:
        input_dir (Path): Directory containing processed task files.
        output_dir (Path): Directory where cleaned corpus and stats will be saved.
        docs (List[str]): In-memory list of document strings.
        original_count (int): Number of documents before cleaning.
        before_tokens (int): Total token count before cleaning.
        after_tokens (int): Total token count after cleaning.
    """

    def __init__(self):
        """
        Initialize the cleaner with input/output directories and parameters.

        Creates the output directory if it does not exist and logs the
        configuration parameters for reproducibility.
        """
        self.input_dir = INPUT_PATH
        self.output_dir = OUTPUT_PATH
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.docs: List[str] = []
        self.original_count = 0
        self.before_tokens = 0
        self.after_tokens = 0
        logging.info(f"Input directory: {self.input_dir}")
        logging.info(f"Output directory: {self.output_dir}")
        logging.info(
            f"Parameters: MINHASH_THRESHOLD={MINHASH_THRESHOLD}, "
            f"NGRAM_SIZE={NGRAM_SIZE}, MAX_NGRAM_REPEATS={MAX_NGRAM_REPEATS}"
        )

    def _ensure_string(self, value: Union[str, dict, list, None]) -> str:
        """
        Normalize a value to a string.

        Args:
            value (Union[str, dict, list, None]): Input value to normalize.

        Returns:
            str: String representation of the input, JSON-encoded if necessary.
        """
        if isinstance(value, str):
            return value
        if value is None:
            return ""
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)

    def load_data(self):
        """
        Load documents from configured sources.

        Sources:
            - OCR-processed PDF text files.
            - arXiv JSON file (list or dict format).
            - Talks transcripts in JSONL format.

        Populates:
            self.docs
            self.original_count
            self.before_tokens

        Logs:
            Number of documents loaded.
        """
        pdf_dir = self.input_dir / PDF_OCR_FOLDER
        pdf_files = list(pdf_dir.glob("*.txt"))
        for f in pdf_files:
            try:
                self.docs.append(f.read_text(encoding="utf-8", errors="ignore"))
            except Exception as e:
                logging.warning(f"Failed to read {f}: {e}")

        arxiv_path = self.input_dir / ARXIV_JSON_FILE
        if arxiv_path.exists():
            try:
                with open(arxiv_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.docs.extend(self._ensure_string(v) for v in data.values())
                    elif isinstance(data, list):
                        self.docs.extend(self._ensure_string(v) for v in data)
                    else:
                        logging.warning(f"Unexpected format in {arxiv_path}")
            except Exception as e:
                logging.warning(f"Failed to load {arxiv_path}: {e}")

        talks_path = self.input_dir / TALKS_JSONL_FILE
        if talks_path.exists():
            with open(talks_path, encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        self.docs.append(self._ensure_string(obj.get("text", "")))
                    except json.JSONDecodeError:
                        logging.warning("Skipping invalid JSON line in talks file.")

        self.docs = [self._ensure_string(d) for d in self.docs]
        self.original_count = len(self.docs)
        self.before_tokens = sum(len(d.split()) for d in self.docs)
        logging.info(f"Loaded {self.original_count} documents")

    def filter_language(self):
        """
        Filter documents by language.

        Keeps only documents detected as English using `langdetect`.
        Empty or undecodable documents are skipped.

        Logs:
            Number of documents before and after filtering.
        """
        before = len(self.docs)
        filtered_docs = []
        for d in self.docs:
            text_sample = d.strip()[:500]
            if not text_sample:
                continue
            try:
                if detect(text_sample) == "en":
                    filtered_docs.append(d)
            except Exception:
                continue
        self.docs = filtered_docs
        after = len(self.docs)
        logging.info(f"Language filter: {before} -> {after} documents")

    def strip_html(self):
        """
        Remove HTML tags from all documents.

        Uses BeautifulSoup to extract visible text content.
        """
        self.docs = [BeautifulSoup(d, "html.parser").get_text() for d in self.docs]

    def deduplicate(self):
        """
        Remove near-duplicate documents using MinHash LSH.

        Documents are tokenized into 3-word shingles (configurable) and hashed.
        Only the first occurrence of a near-duplicate is kept.

        Logs:
            Number of documents before and after deduplication.
        """
        before = len(self.docs)

        def get_minhash(text):
            m = MinHash(num_perm=128)
            tokens = text.split()
            for i in range(len(tokens) - 2):
                shingle = " ".join(tokens[i : i + 3])
                m.update(shingle.encode("utf8"))
            return m

        lsh = MinHashLSH(threshold=MINHASH_THRESHOLD, num_perm=128)
        unique_docs = []
        for i, doc in enumerate(self.docs):
            mh = get_minhash(doc)
            if not lsh.query(mh):
                lsh.insert(f"doc_{i}", mh)
                unique_docs.append(doc)
        self.docs = unique_docs
        after = len(self.docs)
        logging.info(f"Deduplication: {before} -> {after} documents")

    def remove_pii(self):
        """
        Mask personally identifiable information (PII).

        Replaces:
            - Emails with [EMAIL]
            - Credit card numbers with [CREDIT_CARD]
            - Phone numbers with [PHONE]
        """
        email_re = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
        cc_re = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
        phone_re = re.compile(
            r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b"
        )

        def sub(text: str) -> str:
            """Apply PII substitutions to a single document string."""
            return phone_re.sub(
                "[PHONE]", cc_re.sub("[CREDIT_CARD]", email_re.sub("[EMAIL]", text))
            )

        self.docs = [sub(doc) for doc in self.docs]

    def remove_repetitive_ngrams(self):
        """
        Remove excessively repeated n-grams from documents.

        This step identifies n-grams of size `NGRAM_SIZE` that occur more than
        `MAX_NGRAM_REPEATS` times in a document and collapses them to a single
        occurrence. This helps reduce noise from OCR errors or spammy content.

        Notes:
            - Tokenization is whitespace-based.
            - Regex patterns are dynamically generated for each repeated n-gram.
            - Invalid regex patterns are skipped with a warning.
        """

        def clean(text: str) -> str:
            tokens = text.split()
            counts = Counter(
                tuple(tokens[i : i + NGRAM_SIZE])
                for i in range(len(tokens) - NGRAM_SIZE + 1)
            )
            for ngram, count in counts.items():
                if count > MAX_NGRAM_REPEATS:
                    escaped_tokens = [re.escape(tok) for tok in ngram]
                    pattern = "(?:\\b" + "\\s+".join(escaped_tokens) + "\\b\\s*)+"
                    try:
                        regex = re.compile(pattern)
                        text = regex.sub(" ".join(ngram) + " ", text)
                    except re.error as e:
                        logging.warning(
                            f"Skipping invalid regex for ngram {ngram}: {e}"
                        )
            return text

        self.docs = [clean(doc) for doc in self.docs]

    def save_outputs(self):
        """
        Save cleaned corpus and statistics to the output directory.

        Outputs:
            - `clean_corpus.txt`: One cleaned document per line.
            - `stats.md`: Markdown file with cleaning statistics.

        Statistics include:
            - Original document count
            - Document count after deduplication
            - Token counts before and after cleaning
            - Percentage of tokens removed
        """
        self.after_tokens = sum(len(d.split()) for d in self.docs)
        removal_pct = (
            100 * (self.before_tokens - self.after_tokens) / self.before_tokens
            if self.before_tokens
            else 0
        )

        clean_path = self.output_dir / "clean_corpus.txt"
        stats_path = self.output_dir / "stats.md"

        with open(clean_path, "w", encoding="utf-8") as f:
            for doc in self.docs:
                f.write(doc.strip() + "\n")

        with open(stats_path, "w", encoding="utf-8") as f:
            f.write(f"# Cleaning Stats\n")
            f.write(f"- Original docs: {self.original_count}\n")
            f.write(f"- After deduplication: {len(self.docs)}\n")
            f.write(f"- Tokens before: {self.before_tokens}\n")
            f.write(f"- Tokens after: {self.after_tokens}\n")
            f.write(f"- Removal percentage: {removal_pct:.2f}%\n")

        logging.info(f"Outputs saved: {clean_path}, {stats_path}")

    def run(self):
        """
        Execute the full cleaning pipeline in sequence.

        Steps:
            1. Load data from all sources.
            2. Filter by language.
            3. Strip HTML tags.
            4. Deduplicate near-duplicate documents.
            5. Remove PII.
            6. Remove repetitive n-grams.
            7. Save cleaned corpus and stats.

        This is the main orchestration method for the cleaning process.
        """
        self.load_data()
        self.filter_language()
        self.strip_html()
        self.deduplicate()
        self.remove_pii()
        self.remove_repetitive_ngrams()
        self.save_outputs()


def main():
    """
    Entry point for the data cleaning script.

    Initializes the `EndToEndCleaner` and runs the cleaning pipeline.
    Handles unexpected exceptions by logging them and exiting with a
    non-zero status code.

    Typical usage:
        $ python data_cleaner.py
    """
    logging.info("Data cleaning script started.")
    try:
        cleaner = EndToEndCleaner()
        cleaner.run()
        logging.info("Data cleaning script finished successfully.")
    except Exception as e:
        logging.exception(f"Unhandled error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
