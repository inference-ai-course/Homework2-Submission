# Task 1 using selenium screenshot and ocr (pytesseract) to extract key information (title, authors, abstract, date) from arXiv papers 
# OR using trafilatura to extract key information (title, authors, abstract, date) from arXiv papers

# arXiv Paper Abstract Scraper
# tesseract image.png output -l spa
import requests
import xml.etree.ElementTree as ET
import trafilatura
import pytesseract
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
import time
import re


def query_arxiv(category, max_results=50):  # Limited to 50 for size; change to 200 if needed
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    entries = []
    # This line is using the ElementTree module to parse the XML response from the arXiv API. 
    # The XML response is a list of entries, each containing information about a paper.
    # The line is using the findall method to find all the entries in the XML response.
    # The findall method returns a list of all elements in the document that match the specified tag name or path.
    # The argument to findall is a string that specifies the tag name or path to search for.
    # The tag name or path is specified using the {http://www.w3.org/2005/Atom} namespace prefix.
    # This line is using the namespace prefix to find all the entries in the XML response.
    # The loop then iterates over each entry and extracts the relevant information such as the URL, title, authors, and date.
    # The information is then stored in a dictionary for each paper and added to the entries list.
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        paper = {
            'url': entry.find('{http://www.w3.org/2005/Atom}id').text,
            'title': entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
            'abstract': '',  # To be filled by OCR
            'authors': [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')],
            'date': entry.find('{http://www.w3.org/2005/Atom}published').text
        }
        entries.append(paper)
    return entries

def scrape_with_trafilatura(url):
    response = requests.get(url)
    text = trafilatura.extract(response.text)
    return text

# def parse_trafilatura(raw_text, url=None):
#     # Extract title (after "Title:")
#     title_match = re.search(r'Title:(.*?)(?=View PDF|Abstract:|Submission|$)', raw_text, re.DOTALL)
#     if title_match:
#         title = title_match.group(1).strip()
    
#     # Extract abstract (after "Abstract:" until "Submission history" or similar)
#     abstract_match = re.search(r'Abstract:(.*?)(?=Current browse context|Change to browse by|Submission history|References|Bibliographic|$)', raw_text, re.DOTALL)
#     if abstract_match:
#         abstract = abstract_match.group(1).strip()
    
#     # Extract authors (simple heuristic: names before "View PDF" or in title area)
#     # For this example: "G.E. Volovik."
#     author_match = re.search(r'From:(.*?)(?=\[view email\]|References|$)', clean_text, re.DOTALL)
#     if author_match:
#         authors_text = author_match.group(1).strip()
#         authors = [a.strip() for a in authors_text.split(',') if a.strip()]
#     else:
#         authors = []
    
#     # Extract date (from "Submitted on" or "last revised")
#     date_match = re.search(r'Submitted on (\d{1,2} \w{3} \d{4})', raw_text)
#     if date_match:
#         date = date_match.group(1)
#     else:
#         date_match = re.search(r'last revised (\d{1,2} \w{3} \d{4})', raw_text)
#         if date_match:
#             date = date_match.group(1)
    
#     # Fallback: If no date, use ISO from text if present
#     if not date:
#         iso_match = re.search(r'\d{4}-\d{2}-\d{2}', raw_text)
#         if iso_match:
#             date = iso_match.group(0)
    
#     return {
#         "url": url or "http://arxiv.org/abs/unknown",  # Replace with actual
#         "title": title,
#         "abstract": abstract,
#         "authors": authors,
#         "date": date
#     }

def take_screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless for speed
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(2)  # Wait for load
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    return screenshot

def extract_abstract_from_ocr(ocr_text):
    # Simple heuristic: Look for "Abstract" and extract following text until next section
    match = re.search(r'Abstract\s*(.*?)(?:\n\n|\n[A-Z]|$)', ocr_text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ocr_text[:500]  # Fallback to first 500 chars

if __name__ == "__main__":
    papers_ocr = query_arxiv('cs.CL', 200)  # Use 50 to keep under 1MB; set to 200 if storage allows
    papers_trafilatura = []
    for paper_ocr in papers_ocr:
        url = paper_ocr['url']
        # Scrape and clean (not used in JSON, but per instruction)
        clean_text = scrape_with_trafilatura(url)
        # paper_trafilatura = parse_trafilatura(clean_text, url)
        # papers_trafilatura.append(paper_trafilatura)
        # Take screenshot and OCR
        screenshot = take_screenshot(url)
        img = Image.open(BytesIO(screenshot))
        ocr_text = pytesseract.image_to_string(img)
        paper_ocr['abstract'] = extract_abstract_from_ocr(ocr_text)

    with open('arxiv_clean_ocr.json', 'w') as f:
        json.dump(papers_ocr, f, indent=4)

    # with open('arxiv_clean_trafilatura.json', 'w') as f:
    #     json.dump(papers_trafilatura, f, indent=4)    

    # size = os.path.getsize('arxiv_clean.json')
    # print(f"JSON saved. Size: {size} bytes. Ensure ≤1MB; adjust paper count if needed.")