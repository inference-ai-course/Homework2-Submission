import requests
import trafilatura
from bs4 import BeautifulSoup
import logging

from .arxiv_search import make_request_with_retries

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()])

def process_arxiv_url_with_trafilatura(url: str) -> dict:
    """
    Scrapes a single arXiv abstract page. It uses BeautifulSoup for precise metadata
    extraction (title, authors, date) and Trafilatura to clean the main text content,
    which is the abstract.

    Args:
        url (str): The URL of the arXiv abstract page.

    Returns:
        dict: A dictionary containing the scraped data (url, title, abstract, authors, date).
              Returns an empty dictionary if scraping fails.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        response = make_request_with_retries(url, headers=headers)
        if not response or not response.text:
            logging.warning(f"No response or empty content from {url}")
            return {}

        html_content = response.text
        
        # Use Trafilatura to extract and clean the main content (the abstract)
        # On arXiv abstract pages, the main text block is the abstract itself.
        abstract_text = trafilatura.extract(html_content, include_comments=False, include_tables=False)
        
        # Use BeautifulSoup for precise extraction of other metadata
        soup = BeautifulSoup(html_content, "html.parser")

        title_tag = soup.find("h1", class_="title")
        authors_tag = soup.find("div", class_="authors")
        date_tag = soup.find("div", class_="dateline")

        return {
            "url": url,
            "title": title_tag.get_text(strip=True).replace("Title:", "") if title_tag else "N/A",
            "abstract": abstract_text.strip() if abstract_text else "N/A",
            "authors": authors_tag.get_text(strip=True).replace("Authors:", "") if authors_tag else "N/A",
            "date": date_tag.get_text(strip=True) if date_tag else "N/A"
        }

    except Exception as e:
        logging.error(f"Error processing {url} with Trafilatura: {e}")
        return {}
