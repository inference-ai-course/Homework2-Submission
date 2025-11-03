#!/usr/bin/env python3
"""
data_cleaner.py
Module 4: End-to-End Data Cleaning and Deduplication
Merges outputs from modules 1-3 and performs comprehensive cleaning.
Christine Zhao
2025-11-02
"""

import json
import os
import re
from typing import List, Dict, Set
from langdetect import detect, LangDetectException
from datasketch import MinHash, MinHashLSH
from collections import Counter


class DataCleaner:
    """Cleans and deduplicates text data from multiple sources."""

    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize the data cleaner.

        Args:
            similarity_threshold: Similarity threshold for deduplication (0-1)
        """
        self.similarity_threshold = similarity_threshold
        self.documents = []
        self.stats = {
            "total_docs": 0,
            "after_language_filter": 0,
            "after_deduplication": 0,
            "after_pii_removal": 0,
            "after_ngram_filter": 0,
            "total_tokens_before": 0,
            "total_tokens_after": 0
        }

    def load_arxiv_data(self, json_path: str = "../module1_scraper/arxiv_clean.json"):
        """Load data from arXiv scraper (Module 1)."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                papers = json.load(f)

            for paper in papers:
                text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                self.documents.append({
                    'source': 'arxiv',
                    'text': text,
                    'metadata': paper
                })

            print(f"Loaded {len(papers)} papers from arXiv data.")

        except FileNotFoundError:
            print(f"Warning: {json_path} not found. Skipping arXiv data.")

    def load_pdf_ocr_data(self, ocr_dir: str = "../module2_pdf_ocr/pdf_ocr"):
        """Load data from PDF OCR (Module 2)."""
        try:
            if not os.path.exists(ocr_dir):
                print(f"Warning: {ocr_dir} not found. Skipping PDF OCR data.")
                return

            txt_files = [f for f in os.listdir(ocr_dir) if f.endswith('.txt')]

            for filename in txt_files:
                filepath = os.path.join(ocr_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()

                self.documents.append({
                    'source': 'pdf_ocr',
                    'text': text,
                    'metadata': {'filename': filename}
                })

            print(f"Loaded {len(txt_files)} documents from PDF OCR data.")

        except Exception as e:
            print(f"Error loading PDF OCR data: {e}")

    def load_transcript_data(self, jsonl_path: str = "../module3_asr/talks_transcripts.jsonl"):
        """Load data from ASR transcripts (Module 3)."""
        try:
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    transcript = json.loads(line)
                    text = transcript.get('full_text', '')

                    self.documents.append({
                        'source': 'transcript',
                        'text': text,
                        'metadata': transcript
                    })

            print(f"Loaded transcripts from {jsonl_path}.")

        except FileNotFoundError:
            print(f"Warning: {jsonl_path} not found. Skipping transcript data.")

    def detect_language(self, text: str) -> str:
        """
        Detect language of text.

        Args:
            text: Input text

        Returns:
            Language code (e.g., 'en', 'es')
        """
        try:
            return detect(text)
        except LangDetectException:
            return "unknown"

    def filter_by_language(self, target_lang: str = "en"):
        """
        Filter documents by language.

        Args:
            target_lang: Target language code (default: 'en')
        """
        print(f"\nFiltering documents by language: {target_lang}")

        filtered_docs = []
        for doc in self.documents:
            text = doc['text']
            if len(text.strip()) < 50:  # Skip very short texts
                continue

            lang = self.detect_language(text)
            if lang == target_lang:
                filtered_docs.append(doc)

        print(f"Kept {len(filtered_docs)}/{len(self.documents)} documents after language filtering.")
        self.documents = filtered_docs
        self.stats["after_language_filter"] = len(self.documents)

    def strip_html_noise(self):
        """Remove HTML tags and other noise from text."""
        print("\nRemoving HTML noise and cleaning text...")

        html_pattern = re.compile(r'<[^>]+>')

        for doc in self.documents:
            text = doc['text']

            # Remove HTML tags
            text = html_pattern.sub('', text)

            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)

            # Remove special characters (keep basic punctuation)
            text = re.sub(r'[^\w\s.,!?;:\-\'\"]', ' ', text)

            doc['text'] = text.strip()

    def create_minhash(self, text: str, num_perm: int = 128) -> MinHash:
        """
        Create MinHash for a document.

        Args:
            text: Input text
            num_perm: Number of permutations

        Returns:
            MinHash object
        """
        minhash = MinHash(num_perm=num_perm)

        # Tokenize by words
        words = text.lower().split()

        # Create shingles (3-grams)
        for i in range(len(words) - 2):
            shingle = ' '.join(words[i:i+3])
            minhash.update(shingle.encode('utf-8'))

        return minhash

    def deduplicate_minhash(self):
        """Deduplicate documents using MinHash LSH."""
        print(f"\nDeduplicating with MinHash (threshold: {self.similarity_threshold})...")

        num_perm = 128
        lsh = MinHashLSH(threshold=self.similarity_threshold, num_perm=num_perm)

        unique_docs = []
        seen_ids = set()

        for i, doc in enumerate(self.documents):
            text = doc['text']

            if len(text.strip()) < 100:  # Skip very short texts
                continue

            # Create MinHash
            minhash = self.create_minhash(text, num_perm)

            # Query for similar documents
            result = lsh.query(minhash)

            if not result:
                # No similar documents found, add to unique set
                lsh.insert(f"doc_{i}", minhash)
                unique_docs.append(doc)
                seen_ids.add(i)

        print(f"Kept {len(unique_docs)}/{len(self.documents)} documents after deduplication.")
        self.documents = unique_docs
        self.stats["after_deduplication"] = len(self.documents)

    def remove_pii(self):
        """Remove personally identifiable information (PII)."""
        print("\nRemoving PII (emails, phone numbers, credit cards)...")

        # Patterns for PII
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        phone_pattern = re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
        credit_card_pattern = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')

        for doc in self.documents:
            text = doc['text']

            # Remove emails
            text = email_pattern.sub('[EMAIL]', text)

            # Remove phone numbers
            text = phone_pattern.sub('[PHONE]', text)

            # Remove credit card numbers
            text = credit_card_pattern.sub('[CREDIT_CARD]', text)

            doc['text'] = text

        self.stats["after_pii_removal"] = len(self.documents)

    def remove_repetitive_ngrams(self, n: int = 3, max_repetition: int = 3):
        """
        Remove documents with excessive n-gram repetition.

        Args:
            n: N-gram size
            max_repetition: Maximum allowed repetition count
        """
        print(f"\nRemoving documents with repetitive {n}-grams...")

        filtered_docs = []

        for doc in self.documents:
            text = doc['text']
            words = text.split()

            if len(words) < n:
                filtered_docs.append(doc)
                continue

            # Count n-grams
            ngrams = [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]
            ngram_counts = Counter(ngrams)

            # Check for excessive repetition
            max_count = max(ngram_counts.values()) if ngram_counts else 0

            if max_count <= max_repetition:
                filtered_docs.append(doc)

        print(f"Kept {len(filtered_docs)}/{len(self.documents)} documents after n-gram filtering.")
        self.documents = filtered_docs
        self.stats["after_ngram_filter"] = len(self.documents)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text (simple word-based)."""
        return len(text.split())

    def clean_pipeline(self):
        """Run the complete cleaning pipeline."""
        print("\n" + "="*60)
        print("Starting Data Cleaning Pipeline")
        print("="*60)

        # Load all data
        self.load_arxiv_data()
        self.load_pdf_ocr_data()
        self.load_transcript_data()

        self.stats["total_docs"] = len(self.documents)
        print(f"\nTotal documents loaded: {self.stats['total_docs']}")

        # Count initial tokens
        self.stats["total_tokens_before"] = sum(
            self.count_tokens(doc['text']) for doc in self.documents
        )

        # Run cleaning steps
        self.filter_by_language(target_lang="en")
        self.strip_html_noise()
        self.deduplicate_minhash()
        self.remove_pii()
        self.remove_repetitive_ngrams()

        # Count final tokens
        self.stats["total_tokens_after"] = sum(
            self.count_tokens(doc['text']) for doc in self.documents
        )

        print("\n" + "="*60)
        print("Cleaning Pipeline Completed")
        print("="*60)

    def save_clean_corpus(self, output_file: str = "clean_corpus.txt"):
        """Save cleaned corpus to text file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, doc in enumerate(self.documents, 1):
                f.write(f"--- Document {i} (Source: {doc['source']}) ---\n")
                f.write(doc['text'])
                f.write("\n\n")

        print(f"\nCleaned corpus saved to: {output_file}")

    def save_stats(self, stats_file: str = "stats.md"):
        """Save cleaning statistics to markdown file."""
        removal_percentage = 0
        if self.stats["total_docs"] > 0:
            removed = self.stats["total_docs"] - self.stats["after_ngram_filter"]
            removal_percentage = (removed / self.stats["total_docs"]) * 100

        token_reduction = 0
        if self.stats["total_tokens_before"] > 0:
            token_reduction = (
                (self.stats["total_tokens_before"] - self.stats["total_tokens_after"])
                / self.stats["total_tokens_before"] * 100
            )

        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("# Data Cleaning Statistics\n\n")
            f.write("## Document Counts\n\n")
            f.write(f"- **Total documents loaded**: {self.stats['total_docs']}\n")
            f.write(f"- **After language filtering**: {self.stats['after_language_filter']}\n")
            f.write(f"- **After deduplication**: {self.stats['after_deduplication']}\n")
            f.write(f"- **After PII removal**: {self.stats['after_pii_removal']}\n")
            f.write(f"- **Final document count**: {self.stats['after_ngram_filter']}\n\n")

            f.write("## Token Counts\n\n")
            f.write(f"- **Total tokens before cleaning**: {self.stats['total_tokens_before']:,}\n")
            f.write(f"- **Total tokens after cleaning**: {self.stats['total_tokens_after']:,}\n")
            f.write(f"- **Token reduction**: {token_reduction:.2f}%\n\n")

            f.write("## Removal Statistics\n\n")
            f.write(f"- **Documents removed**: {self.stats['total_docs'] - self.stats['after_ngram_filter']}\n")
            f.write(f"- **Removal percentage**: {removal_percentage:.2f}%\n")

        print(f"Statistics saved to: {stats_file}")


def main():
    """Main function to run data cleaning pipeline."""
    cleaner = DataCleaner(similarity_threshold=0.7)

    # Run cleaning pipeline
    cleaner.clean_pipeline()

    # Save outputs
    cleaner.save_clean_corpus("clean_corpus.txt")
    cleaner.save_stats("stats.md")

    print("\n" + "="*60)
    print("Data cleaning completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
