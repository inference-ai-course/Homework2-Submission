# ArXiv Search and Scraper

This project provides a set of Python utilities to search, scrape, and download research papers from [arXiv](https://arxiv.org/).

## Features

*   Build custom search URLs for arXiv.
*   Scrape search results and save them to JSON files.
*   Scrape detailed metadata from paper abstract pages.
*   Download PDF versions of papers using their arXiv ID.
*   Supports multithreading for faster scraping and downloading.

## How to Use

The main module is `src/utils/arxiv_search.py`. Here is a typical workflow for using the utilities.

### 1. Build a Search URL

First, you need to construct a search URL. You can specify a query, subject, and the number of results.

```python
import src.utils.arxiv_search as arxiv_search

# Define topics to search for
topics = [
    "attention is all you need",
    "machine learning in the modern era"
]

urls = []
for topic in topics:
    urls.append(arxiv_search.build_arxiv_search_url(query=topic, size=20))

print(urls)
```

### 2. Scrape Search Results

Once you have the URLs, you can scrape the search results. The scraper can run in the background to avoid blocking the main thread.

```python
import os
import time
import src.utils.arxiv_search as arxiv_search

# Prepare directory for scraped data
scraped_directory = "data/scraped"
os.makedirs(scraped_directory, exist_ok=True)

output_files = []
for index, url in enumerate(urls):
    file_location = f"{scraped_directory}/{index}_scraped.json"
    # Run scraper in a background thread
    arxiv_search.run_scraper_in_background(url=url, output_file=file_location)
    time.sleep(3) # Be respectful to arXiv's servers
    output_files.append(file_location)

print(f"Scraping tasks started. Output will be saved to: {output_files}")
```

### 3. Scrape Detailed Metadata

From the initial scraped JSON files, you can then scrape the detailed metadata from each paper's abstract page. This is done using a threaded function for efficiency.

```python
import src.utils.arxiv_search as arxiv_search

pages_metadata = []
for file_path in output_files:
    # Use the threaded function to scrape details
    pages_metadata.extend(arxiv_search.scrape_arxiv_details_from_json_threaded(file_path))

print(f"Found metadata for {len(pages_metadata)} papers.")
```

### 4. Save Enriched Metadata

Save the combined list of detailed metadata to a new JSON file. This file will contain enriched information about each paper.

```python
import os
import src.utils.arxiv_search as arxiv_search

enriched_data_dir = "data/enriched"
os.makedirs(enriched_data_dir, exist_ok=True)

metadata_file = f"{enriched_data_dir}/papers_metadata.json"
arxiv_search.save_arxiv_scraped_details(results=pages_metadata, output_file=metadata_file)

print(f"Saved enriched metadata to {metadata_file}")
```

### 5. Download PDFs

Finally, you can download the PDF for each paper using the enriched metadata file. The function will extract the arXiv ID from the paper's URL and download the corresponding PDF.

```python
import os
import src.utils.arxiv_search as arxiv_search

pdf_dir = "data/pdfs/arxiv"
os.makedirs(pdf_dir, exist_ok=True)

# Download PDFs for all papers in the metadata file
arxiv_search.get_pdf_arxiv(cleaned_json=metadata_file, save_dir=pdf_dir)
```

You can also download a single PDF if you know the arXiv ID.

```python
import os
import src.utils.arxiv_search as arxiv_search

pdf_dir = "data/pdfs/arxiv"
os.makedirs(pdf_dir, exist_ok=True)

# Example: Download a specific paper by its arXiv ID
arxiv_search.download_pdf("2510.26641", save_dir=pdf_dir)
