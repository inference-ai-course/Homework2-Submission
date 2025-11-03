#!/usr/bin/env python3
"""
arxiv_scraper.py
Module 1: arXiv Paper Abstract Scraper
Scrapes latest papers from arXiv, extracts abstracts using Trafilatura,
and saves results as JSON.
Christine Zhao
2025-11-02
"""

import json
import time
import requests
from bs4 import BeautifulSoup
import trafilatura
from datetime import datetime
from typing import List, Dict
import re


class ArxivScraper:
    """Scraper for arXiv papers with abstract extraction."""

    def __init__(self, category: str = "cs.CL", max_papers: int = 200):
        """
        Initialize the scraper.

        Args:
            category: arXiv category (e.g., 'cs.CL', 'cs.AI')
            max_papers: Maximum number of papers to scrape
        """
        self.category = category
        self.max_papers = max_papers
        self.base_url = "https://arxiv.org"
        self.papers = []

    def get_paper_list(self) -> List[str]:
        """
        Fetch list of paper IDs from arXiv category.

        Returns:
            List of paper URLs
        """
        paper_urls = []
        start = 0
        papers_per_page = 50

        print(f"Fetching papers from category: {self.category}")

        while len(paper_urls) < self.max_papers:
            url = f"{self.base_url}/list/{self.category}/recent?skip={start}&show={papers_per_page}"

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all paper links
                links = soup.find_all('a', title='Abstract')

                if not links:
                    print("No more papers found.")
                    break

                for link in links:
                    if len(paper_urls) >= self.max_papers:
                        break
                    href = link.get('href')
                    if href:
                        full_url = f"{self.base_url}{href}"
                        paper_urls.append(full_url)

                print(f"Collected {len(paper_urls)} paper URLs...")
                start += papers_per_page
                time.sleep(1)  # Be polite to the server

            except Exception as e:
                print(f"Error fetching paper list: {e}")
                break

        return paper_urls[:self.max_papers]

    def extract_paper_info(self, url: str) -> Dict:
        """
        Extract paper information from arXiv abstract page.

        Args:
            url: URL of the paper abstract page

        Returns:
            Dictionary with paper information
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Use Trafilatura for content extraction
            extracted = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=False,
                output_format='json'
            )

            # Parse with BeautifulSoup for structured extraction
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_tag = soup.find('h1', class_='title mathjax')
            title = title_tag.get_text(strip=True).replace('Title:', '').strip() if title_tag else "N/A"

            # Extract authors
            authors_tag = soup.find('div', class_='authors')
            authors = []
            if authors_tag:
                author_links = authors_tag.find_all('a')
                authors = [a.get_text(strip=True) for a in author_links]

            # Extract abstract
            abstract_tag = soup.find('blockquote', class_='abstract mathjax')
            abstract = ""
            if abstract_tag:
                abstract = abstract_tag.get_text(strip=True).replace('Abstract:', '').strip()

            # Extract date
            date_tag = soup.find('div', class_='dateline')
            date = date_tag.get_text(strip=True) if date_tag else "N/A"

            # Extract arXiv ID from URL
            arxiv_id = url.split('/')[-1]

            paper_data = {
                'url': url,
                'arxiv_id': arxiv_id,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'date': date
            }

            return paper_data

        except Exception as e:
            print(f"Error extracting paper info from {url}: {e}")
            return None

    def scrape(self) -> List[Dict]:
        """
        Main scraping function.

        Returns:
            List of paper dictionaries
        """
        print("Starting arXiv scraper...")
        paper_urls = self.get_paper_list()

        print(f"\nScraping {len(paper_urls)} papers...")
        for i, url in enumerate(paper_urls, 1):
            print(f"Processing paper {i}/{len(paper_urls)}: {url}")

            paper_data = self.extract_paper_info(url)
            if paper_data:
                self.papers.append(paper_data)

            # Be polite to the server
            time.sleep(0.5)

        print(f"\nSuccessfully scraped {len(self.papers)} papers.")
        return self.papers

    def save_to_json(self, output_file: str = "arxiv_clean.json"):
        """
        Save scraped papers to JSON file.

        Args:
            output_file: Output JSON filename
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.papers, f, ensure_ascii=False, indent=2)

        # Check file size
        import os
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)

        print(f"\nSaved to {output_file}")
        print(f"File size: {file_size_mb:.2f} MB")

        if file_size_mb > 1:
            print("WARNING: File size exceeds 1MB limit. Consider reducing the number of papers.")


def main():
    """Main function to run the scraper."""
    # Initialize scraper for cs.CL (Computation and Language) category
    scraper = ArxivScraper(category="cs.CL", max_papers=200)

    # Scrape papers
    papers = scraper.scrape()

    # Save to JSON
    scraper.save_to_json("arxiv_clean.json")

    print("\n" + "="*50)
    print("Scraping completed successfully!")
    print(f"Total papers scraped: {len(papers)}")
    print("="*50)


if __name__ == "__main__":
    main()
