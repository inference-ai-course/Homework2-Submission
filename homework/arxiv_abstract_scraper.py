"""
arxiv_scraper.py

Brief description:
    Fetches recent academic papers from the arXiv API for a given category,
    extracts their abstracts, and saves them to a JSON file under a size limit.

Detailed description:
    - Queries the arXiv API for the most recent papers in a configurable category.
    - Retrieves HTML pages for each paper and extracts abstracts using `trafilatura`.
    - Falls back to API-provided abstracts if extraction fails.
    - Saves results to a JSON file, truncating abstracts or reducing record count
      if the file exceeds a configured size limit.

Usage:
    python arxiv_scraper.py

Environment variables (optional):
    PROCESSED_TASKS_FOLDER   - Output folder for processed JSON (default: "02_processed_tasks")
    ARXIV_CATEGORY           - arXiv search category (default: "cs.CL")
    ARXIV_MAX_RESULTS        - Max number of papers to fetch (default: 200)
    ARXIV_OUTPUT_FILE        - Output JSON filename (default: "arxiv_clean.json")
    ARXIV_SIZE_LIMIT         - Max JSON file size in bytes (default: 1,000,000)
    REQUEST_TIMEOUT          - HTTP request timeout in seconds (default: 10)
    ARXIV_POLITE_DELAY       - Delay between API requests in seconds (default: 2)

Dependencies:
    - arxiv
    - requests
    - trafilatura
    - python-dotenv
"""

import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import arxiv
import requests
import trafilatura
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s",
)

ARXIV_OUTPUT_FOLDER = os.getenv("PROCESSED_TASKS_FOLDER", "02_processed_tasks")
ARXIV_SEARCH_CATEGORY = os.getenv("ARXIV_CATEGORY", "cs.CL")
ARXIV_MAX_PAPERS = int(os.getenv("ARXIV_MAX_RESULTS", "200"))
ARXIV_OUTPUT_FILENAME = os.getenv("ARXIV_OUTPUT_FILE", "arxiv_clean.json")
ARXIV_JSON_SIZE_LIMIT_BYTES = int(os.getenv("ARXIV_SIZE_LIMIT", "1000000"))
HTTP_REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT", "10"))
ARXIV_REQUEST_DELAY_SECONDS = int(os.getenv("ARXIV_POLITE_DELAY", "2"))


@dataclass
class ArxivPaper:
    """
    Represents a single arXiv paper.

    Attributes:
        url (str): Link to the paper's abstract page.
        title (str): Paper title.
        abstract (str): Extracted or fallback abstract text.
        authors (List[str]): List of author names.
        date (str): Publication date in human-readable format.
        pdf_url (Optional[str]): Direct link to the PDF version, if available.
    """

    url: str
    title: str
    abstract: str
    authors: List[str]
    date: str
    pdf_url: Optional[str] = None


class ArxivAbstractScraper:
    """
    Handles fetching, processing, and saving arXiv papers for a given category.

    Workflow:
        1. Fetch results from the arXiv API.
        2. Retrieve HTML and extract abstracts.
        3. Save results to JSON under a size limit.
    """

    def __init__(self) -> None:
        """
        Initialize scraper configuration and ensure output directory exists.
        """
        self.output_dir = BASE_DIR / ARXIV_OUTPUT_FOLDER
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_path = self.output_dir / ARXIV_OUTPUT_FILENAME
        self.search_category = ARXIV_SEARCH_CATEGORY
        self.max_papers = ARXIV_MAX_PAPERS
        self.size_limit_bytes = ARXIV_JSON_SIZE_LIMIT_BYTES
        self.request_timeout_seconds = HTTP_REQUEST_TIMEOUT_SECONDS
        self.polite_delay_seconds = ARXIV_REQUEST_DELAY_SECONDS
        logging.info(f"Output folder: {self.output_dir}")
        logging.info(f"Category: {self.search_category}, Max papers: {self.max_papers}")

    def fetch_results(self) -> List[arxiv.Result]:
        """
        Query the arXiv API for recent papers.

        Returns:
            List[arxiv.Result]: API result objects.
        """
        logging.info(
            f"Fetching up to {self.max_papers} results from '{self.search_category}'"
        )
        start_time = time.time()
        client = arxiv.Client(page_size=100, delay_seconds=self.polite_delay_seconds)
        search = arxiv.Search(
            query=self.search_category,
            max_results=self.max_papers,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        results = list(client.results(search))
        logging.info(
            f"Fetched {len(results)} results in {time.time() - start_time:.2f}s"
        )
        return results

    def get_html(self, url: str) -> str:
        """
        Fetch HTML content for a given URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: Raw HTML content.
        """
        response = requests.get(url, timeout=self.request_timeout_seconds)
        response.raise_for_status()
        return response.text

    def extract_abstract(self, html_text: str, fallback: str) -> str:
        """
        Extract abstract text from HTML.

        Args:
            html_text (str): HTML content of the paper's page.
            fallback (str): Fallback abstract if extraction fails.

        Returns:
            str: Extracted or fallback abstract.
        """
        extracted = trafilatura.extract(html_text)
        return extracted.strip() if extracted else fallback.strip()

    def build_paper(self, result: arxiv.Result) -> ArxivPaper:
        """
        Build an ArxivPaper object from an API result.

        Args:
            result (arxiv.Result): API result object.

        Returns:
            ArxivPaper: Structured paper data.

        Raises:
            ValueError: If required fields are missing.
        """
        html = self.get_html(result.entry_id)
        abstract = self.extract_abstract(html, fallback=result.summary or "")
        if not all(
            [result.entry_id, result.title, abstract, result.authors, result.published]
        ):
            raise ValueError(f"Missing required fields for {result.entry_id}")
        return ArxivPaper(
            url=result.entry_id,
            title=result.title.strip(),
            abstract=abstract,
            authors=[a.name for a in result.authors],
            date=result.published.strftime("%A, %B %d, %Y"),
            pdf_url=getattr(result, "pdf_url", None),
        )

    def save_json_under_limit(self, papers: List[ArxivPaper]) -> None:
        """
        Save papers to JSON, ensuring file size is within limit.

        Strategy:
            1. Save full abstracts.
            2. If too large, truncate abstracts.
            3. If still too large, reduce record count.
        """
        logging.info(
            f"Saving {len(papers)} papers to JSON (limit {self.size_limit_bytes} bytes)"
        )

        def dump_and_size(objs: List[ArxivPaper]) -> Tuple[str, int]:
            data = json.dumps([asdict(p) for p in objs], indent=2, ensure_ascii=False)
            return data, len(data.encode("utf-8"))

        # Attempt full save
        data, size = dump_and_size(papers)
        if size <= self.size_limit_bytes:
            self.output_path.write_text(data, encoding="utf-8")
            logging.info(f"Saved {len(papers)} records")
            return

        # Truncate abstracts
        logging.warning("Size exceeds limit — truncating abstracts")
        avg_over = size / self.size_limit_bytes
        target_len = max(500, int(2000 / avg_over))
        truncated = [
            ArxivPaper(
                **{
                    **asdict(p),
                    "abstract": (
                        (p.abstract[:target_len] + "…")
                        if len(p.abstract) > target_len
                        else p.abstract
                    ),
                }
            )
            for p in papers
        ]
        data, size = dump_and_size(truncated)
        if size <= self.size_limit_bytes:
            self.output_path.write_text(data, encoding="utf-8")
            logging.info(f"Saved {len(truncated)} truncated records")
            return

        # Reduce record count
        logging.warning("Still too large — reducing record count")
        low, high = 1, len(truncated)
        best_data, best_count = None, 0
        while low <= high:
            mid = (low + high) // 2
            subset = truncated[:mid]
            data, size = dump_and_size(subset)
            if size <= self.size_limit_bytes:
                best_data, best_count = data, mid
                low = mid + 1
            else:
                high = mid - 1
        if best_data:
            self.output_path.write_text(best_data, encoding="utf-8")
            logging.info(f"Saved {best_count} reduced records")
        else:
            raise ValueError("Unable to fit records under size limit")

    def run(self) -> None:
        """
        Execute the full scraping workflow:
            1. Fetch results from arXiv.
            2. Build structured paper objects.
            3. Save them to JSON under the size limit.
        """
        logging.info("Scraper started")
        results = self.fetch_results()
        papers = []

        for i, result in enumerate(results, start=1):
            try:
                papers.append(self.build_paper(result))
                # Log progress every 20 papers or at the end
                if i % 20 == 0 or i == len(results):
                    logging.info(f"Processed {i}/{len(results)} papers")
                # Small delay to avoid overwhelming the server
                time.sleep(self.polite_delay_seconds / 5)
            except Exception as e:
                logging.warning(f"Skipped [{i}/{len(results)}]: {e}")

        logging.info(f"Processing complete: {len(papers)}/{len(results)} successful")
        self.save_json_under_limit(papers)
        logging.info(f"Output written to: {self.output_path}")


def main() -> None:
    """
    Main entry point for the script.

    Loads environment variables, initializes the scraper, and runs it.
    Exits with a non-zero status code if an unhandled exception occurs.
    """
    try:
        load_dotenv()
        scraper = ArxivAbstractScraper()
        scraper.run()
    except Exception as e:
        logging.error(f"Unhandled error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
