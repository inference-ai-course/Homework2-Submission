import os
import html
import json
import requests
import logging
import threading
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()])


arxiv_subject = ['', 'physics', 'cs', 'math', 'q-bio'] # subject terms on arxiv
arxiv_search_type = ['abstract', 'all', 'title', 'author', 'comments']

# https://arxiv.org/search/?query=deep+learning&searchtype=all&abstracts=show&order=-announced_date_first&size=200
# https://arxiv.org/search/cs?query=deep+learning&searchtype=all&abstracts=show&order=-announced_date_first&size=200

arxiv_search_url = "https://arxiv.org/search/"

def build_arxiv_search_url(subject: str = "cs", query: str ="Deep Learning", searchtype: str = "all", abstracts: str ="show", order: str = "-announced_date_first", size: int = 200) -> str:
    """
    Returns an arxiv search URL for retrieving a latest list of items

    Parameters:
    subject (str): Paper subject of interest.
    query (str): User defined search query e.g. paper name
    searchtype (str): Search type  ['abstract', 'all', 'title', 'author', 'comments', ... ]
    abstracts (str): Show abstract or not
    order (str): order to show
    size (int): number of results to show

    Rerurns:
    str: ArXiv Search URL

    Test:
    >>> url = build_arxiv_search_url(size=34)
    """

    # start building the url.
    arxiv_search_url = "https://arxiv.org/search/"

    # check subject if empty
    if subject.strip():
        arxiv_search_url += subject.strip()

    arxiv_search_url += "?query=" + quote_plus(query.lower().strip()) + "&"
    arxiv_search_url += "searchtype=" + searchtype.lower().strip() + "&"
    arxiv_search_url += "abstracts=" + abstracts.lower().strip() + "&"
    arxiv_search_url += "order=" + order.lower().strip() + "&"

    # control the page size
    if size <= 25:
        size = 25
    elif size > 25 and size <=50:
        size = 50
    elif size > 50 and size <=100:
        size = 100
    else:
        size = 200
    
    # set the size
    arxiv_search_url += "size=" + str(int(size))
    
    # handle if subject is 
    return arxiv_search_url


def scrape_arxiv_url_to_json(url: str, output_file: str = "arxiv_results.json") -> None:
    """
    Scrape arXiv search results from a given URL and save to a JSON file.

    Args:
        url (str): Fully constructed arXiv search URL.
        output_file (str): Filename to save JSON output.
    """
    response = requests.get(url)
    if response.status_code != 200:
        logging.warning(f"Failed to fetch page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    results_list = soup.find("ol", class_="breathe-horizontal")
    results = results_list.find_all("li", class_="arxiv-result") if results_list else []

    papers = []
    for item in results:
        title_tag = item.find("p", class_="title")
        abstract_tag = item.find("span", class_="abstract-full")
        authors_tag = item.find("p", class_="authors")
        link_tag = item.find("p", class_="list-title").find("a")

        paper = {
            "title": title_tag.get_text(strip=True) if title_tag else None,
            "abstract": abstract_tag.get_text(strip=True) if abstract_tag else None,
            "authors": authors_tag.get_text(strip=True) if authors_tag else None,
            "link": link_tag["href"] if link_tag else None
        }
        papers.append(paper)
    
    # Ensure directory exists
    output_dir = os.path.dirname(output_file)
    
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            logging.debug(f"Created directory: {output_dir}")
        except Exception as e:
            logging.error(f"Failed to create directory '{output_dir}': {e}")
            return


    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)

    logging.debug(f"Saved {len(papers)} papers to {output_file}")


def run_scraper_in_background(url: str, output_file: str = "arxiv_results.json") -> None:
    """
    Run in the background

    """
    thread = threading.Thread(target=scrape_arxiv_url_to_json, args=(url, output_file))
    thread.start()
    logging.debug(f"Scraping started in background. Results will be saved to {output_file}.")
