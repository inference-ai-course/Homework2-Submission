# Task 2 
# option1: using pdf2image + Tesseract to extract text
# opion 2: directly use pdfplumber

import requests
import xml.etree.ElementTree as ET
import pytesseract
import json
import re
import pdf2image
import pdfplumber

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

def download_pdf(url):
    pdf_url = url.replace('/abs/', '/pdf/') + '.pdf'  # Convert /abs/ to /pdf/
    response = requests.get(pdf_url)
    if response.status_code == 200:
        return response.content
    return None

# option 1: pdf2image + Tesseract
def scan_pdf_image_to_text(pdf_bytes):
    scan_image=pdf2image.convert_from_bytes(pdf_bytes, dpi=300)
    # grab the first page to get the abstract
    ocr_text = pytesseract.image_to_string(scan_image[0])
    extract_text = extract_abstract_from_ocr(ocr_text)
    return extract_text
    
def extract_abstract_from_ocr(ocr_text):
    # Simple heuristic: Look for "Abstract" and extract following text until next section
    match = re.search(r'Abstract\s*(.*?)(?:\n\n|$)', ocr_text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ocr_text[:500]  # Fallback to first 500 chars



# option 2: pdfplumber
def extract_abstract_from_pdf(pdf_bytes):
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if len(pdf.pages) > 0:
                page_text = pdf.pages[0].extract_text()  # First page
                # Look for Abstract section
                match = re.search(r'Abstract\s*(.*?)(?:\n\n|\n[A-Z]|$)', page_text, re.DOTALL | re.IGNORECASE)
                return match.group(1).strip() if match else page_text[:1000]  # Fallback to first 1000 chars
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return ""


if __name__ == "__main__":
    import io  # For BytesIO
    
    papers = query_arxiv('cs.CL', 200)  # Use 50 for size; set to 200 if needed
    papers_pdfocr = []
    papers_pdfplumber = []
    for paper in papers:
        paper_pdfocr = paper.copy()
        # paper_pdfplumber = paper.copy()
        url = paper['url']
        pdf_bytes = download_pdf(url)
        if pdf_bytes:
            # option 1: pdf2image + Tesseract
            paper_pdfocr['abstract'] = scan_pdf_image_to_text(pdf_bytes)
            # option 2: pdfplumber
            # paper_pdfplumber['abstract'] = extract_abstract_from_pdf(pdf_bytes)
        else:
            paper_pdfocr['abstract'] = "PDF download failed"
            # paper_pdfplumber['abstract'] = "PDF download failed"
    
        papers_pdfocr.append(paper_pdfocr)
        # papers_pdfplumber.append(paper_pdfplumber)
    
    with open('arxiv_clean_pdfocr.json', 'w') as f:
        json.dump(papers_pdfocr, f, indent=4)
    # with open('arxiv_clean_pdftext.json', 'w') as f:
    #     json.dump(papers_pdfplumber, f, indent=4)
