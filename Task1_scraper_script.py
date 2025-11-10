import requests
import trafilatura
from PIL import Image
import pytesseract
import json
import time
import io
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===================== Configuration =====================
CATEGORY = "cs.CL"
MAX_RESULTS = 200
OUTPUT_FILE = "D:/MLE/Homework2-Submission/arxiv_clean.json"
SCREENSHOT_DIR = "D:/MLE/Homework2-Submission/screenshots"
REQUEST_DELAY = 0.5
MAX_JSON_SIZE = 1_000_000

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ===================== Selenium Setup =====================
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # new headless mode for Chrome 109+
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1200x800")
driver = webdriver.Chrome(options=chrome_options)

# ===================== Helper Functions =====================
def fetch_feed(category, max_results=200):
    """Fetch the arXiv RSS feed for a given category"""
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text

def parse_feed(feed_text):
    """Parse RSS feed and extract basic paper info"""
    entries = feed_text.split("<entry>")[1:]
    papers = []
    for entry in entries:
        try:
            title = entry.split("<title>")[1].split("</title>")[0].strip()
            url = entry.split("<id>")[1].split("</id>")[0].replace("http://arxiv.org/abs/", "https://arxiv.org/abs/")
            authors = [a.split("</name>")[0].split(">")[-1] for a in entry.split("<author>")[1:]]
            date = entry.split("<published>")[1].split("</published>")[0]
            papers.append({"title": title, "url": url, "authors": authors, "date": date})
        except Exception:
            continue
    return papers

def fetch_abstract(url, save_screenshot=True, idx=0):
    """Fetch abstract text using HTML cleaning + optional screenshot OCR"""
    try:
        # ---- HTML Cleaning with Trafilatura ----
        html = requests.get(url, timeout=10).text
        text_clean = trafilatura.extract(html)
        abstract = "N/A"
        if text_clean and "Abstract" in text_clean:
            start = text_clean.find("Abstract") + len("Abstract")
            end_candidates = [text_clean.find("\n\n", start), text_clean.find("\n\n\n", start)]
            end_candidates = [e for e in end_candidates if e != -1]
            end = min(end_candidates) if end_candidates else len(text_clean)
            abstract = text_clean[start:end].strip()

        # ---- Selenium Screenshot + OCR ----
        if save_screenshot:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            png = driver.get_screenshot_as_png()
            image = Image.open(io.BytesIO(png))
            image.save(f"{SCREENSHOT_DIR}/paper_{idx}.png")
            ocr_text = pytesseract.image_to_string(image)
            # Optional: combine OCR and cleaned text
            if not abstract or abstract == "N/A":
                if ocr_text.strip():
                    abstract = ocr_text.strip()

        return abstract
    except Exception:
        return "N/A"

# ===================== Main Script =====================
if __name__ == "__main__":
    print(f"Fetching feed for {CATEGORY}...")
    feed_text = fetch_feed(CATEGORY, MAX_RESULTS)
    papers = parse_feed(feed_text)

    print(f"Found {len(papers)} papers. Processing abstracts...")
    for i, paper in enumerate(papers):
        paper["abstract"] = fetch_abstract(paper["url"], save_screenshot=True, idx=i)
        print(f"[{i+1}/{len(papers)}] {paper['title'][:200]} ...")
        time.sleep(REQUEST_DELAY)

    # Ensure JSON ≤1MB
    while True:
        data = json.dumps(papers, ensure_ascii=False, indent=2)
        if len(data.encode("utf-8")) <= MAX_JSON_SIZE:
            break
        # Truncate the longest abstract
        longest = max(papers, key=lambda p: len(p.get("abstract","")))
        longest["abstract"] = longest["abstract"][:len(longest["abstract"])//2]

    # Save JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(data)

    print(f"Saved {len(papers)} papers to {OUTPUT_FILE}")
    driver.quit()
