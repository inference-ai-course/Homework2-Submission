import requests
from bs4 import BeautifulSoup
import trafilatura
import pytesseract
from PIL import Image
from io import BytesIO
import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Config
SUBCATEGORY = "cs.CL"
MAX_PAPERS = 200
OUTPUT_FILE = "arxiv_clean.json"

BASE_URL = f"https://arxiv.org/list/{SUBCATEGORY}/new"

# GET LATEST PAPER LIST
def get_paper_links():
    res = requests.get(BASE_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    abs_links = [
        "https://arxiv.org" + a["href"]
        for a in soup.select("a[href^='/abs/']")
    ]
    # Remove duplicates and limit
    return list(dict.fromkeys(abs_links))[:MAX_PAPERS]

# CLEAN HTML WITH TRAFILATURA -abs_links
def clean_html_with_trafilatura(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        text = trafilatura.extract(downloaded)
        return text
    return None

# OCR FALLBACK VIA SCREENSHOT
def extract_with_ocr(url, driver):
    driver.get(url)
    time.sleep(1.5)
    screenshot = driver.get_screenshot_as_png()
    img = Image.open(BytesIO(screenshot))
    text = pytesseract.image_to_string(img)
    return text

# PARSE METADATA FROM PAGE
def parse_metadata(soup):
    title = soup.find("h1", {"class": "title"}).get_text(strip=True).replace("Title:", "")
    authors = soup.find("div", {"class": "authors"}).get_text(strip=True).replace("Authors:", "")
    date = soup.find("div", {"class": "dateline"}).get_text(strip=True)
    return title, authors, date

# MAIN SCRAPER
def scrape_arxiv():
    links = get_paper_links()
    data = []

    # Initialize headless browser for OCR fallback
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    for i, url in enumerate(links):
        print(f"[{i+1}/{len(links)}] Scraping {url}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        title, authors, date = parse_metadata(soup)
        cleaned_text = clean_html_with_trafilatura(url)

        # Extract abstract
        abstract = ""
        if cleaned_text:
            # Try to find abstract portion
            match = re.search(r"Abstract[:\s]+(.*?)\n", cleaned_text, re.S)
            abstract = match.group(1).strip() if match else cleaned_text[:500]

        # Fallback to OCR if abstract seems empty
        if len(abstract) < 30:
            print("→ Using OCR fallback.")
            abstract = extract_with_ocr(url, driver)

        data.append({
            "url": url,
            "title": title,
            "authors": authors,
            "date": date,
            "abstract": abstract.strip()
        })

        time.sleep(0.5) 

    driver.quit()
    return data

# SAVE JSON
def save_json(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(data)} records to {OUTPUT_FILE}")

if __name__ == "__main__":
    papers = scrape_arxiv()
    save_json(papers)