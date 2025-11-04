# task 4
import json
import re
from langdetect import detect
from datasketch import MinHash, MinHashLSH
from bs4 import BeautifulSoup
import nltk
from collections import Counter
import glob

# Download NLTK data if needed
nltk.download('punkt')

# Function to extract text from JSON files
def load_texts():
    texts = []
    # Task 1 outputs
    for file in ['arxiv_clean_ocr.json', 'arxiv_clean_pdfocr.json']:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if 'abstract' in item and item['abstract']:
                        texts.append(item['abstract'])
        except FileNotFoundError:
            print(f"File {file} not found")

    # Task 3 output
    try:
        for file_path in glob.glob('transcripts/*_transcript.jsonl'):
            with open(file_path, 'r', encoding='utf-8') as f:
                # Each line is a JSON object
                for line in f:
                    item = json.loads(line)
                    transcript_text = ' '.join([seg['text'] for seg in item['transcript']])
                    texts.append(transcript_text)
    except FileNotFoundError:
        print("talks_transcripts.jsonl not found")
    return texts

# Language detection
def filter_english(texts):
    english_texts = []
    for text in texts:
        try:
            if detect(text) == 'en':
                english_texts.append(text)
        except:
            pass
    return english_texts

# Strip HTML
def strip_html(texts):
    cleaned = []
    for text in texts:
        soup = BeautifulSoup(text, 'html.parser')
        cleaned.append(soup.get_text())
    return cleaned

# MinHash deduplication
def deduplicate_texts(texts, threshold=0.7):
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    minhashes = {}
    unique_texts = []
    for i, text in enumerate(texts):
        mh = MinHash(num_perm=128)
        for word in text.split():
            mh.update(word.encode('utf-8'))
        if not lsh.query(mh):
            lsh.insert(f"doc_{i}", mh)
            unique_texts.append(text)
    return unique_texts

# Remove PII
def remove_pii(texts):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    cc_pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    cleaned = []
    for text in texts:
        text = re.sub(email_pattern, '[EMAIL]', text)
        text = re.sub(phone_pattern, '[PHONE]', text)
        text = re.sub(cc_pattern, '[CC]', text)
        cleaned.append(text)
    return cleaned

# Remove repetitive n-grams
def remove_repetitive_ngrams(texts, n=2, threshold=5):
    all_ngrams = []
    for text in texts:
        tokens = nltk.word_tokenize(text.lower())
        ngrams = list(nltk.ngrams(tokens, n))
        all_ngrams.extend(ngrams)
    ngram_counts = Counter(all_ngrams)
    repetitive = {ngram for ngram, count in ngram_counts.items() if count >= threshold}
    
    cleaned = []
    for text in texts:
        tokens = nltk.word_tokenize(text)
        filtered_tokens = []
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            if ngram not in repetitive:
                filtered_tokens.append(tokens[i])
        cleaned.append(' '.join(filtered_tokens))
    return cleaned

# Main
if __name__ == "__main__":
    original_texts = load_texts()
    print(f"Original texts: {len(original_texts)}")
    
    english_texts = filter_english(original_texts)
    print(f"After language filter: {len(english_texts)}")
    
    html_stripped = strip_html(english_texts)
    print(f"After HTML strip: {len(html_stripped)}")
    
    deduped = deduplicate_texts(html_stripped)
    print(f"After dedup: {len(deduped)}")
    
    pii_removed = remove_pii(deduped)
    print(f"After PII removal: {len(pii_removed)}")
    
    final_cleaned = remove_repetitive_ngrams(pii_removed)
    print(f"After n-gram removal: {len(final_cleaned)}")
    
    # Save corpus
    with open('clean_corpus.txt', 'w', encoding='utf-8') as f:
        for text in final_cleaned:
            f.write(text + '\n\n')
    
    # Calculate stats
    original_tokens = sum(len(text.split()) for text in original_texts)
    final_tokens = sum(len(text.split()) for text in final_cleaned)
    removal_percentage = (1 - final_tokens / original_tokens) * 100 if original_tokens > 0 else 0
    
    with open('stats.md', 'w', encoding='utf-8') as f:
        f.write(f"# Data Cleaning Stats\n\n")
        f.write(f"- Original texts: {len(original_texts)}\n")
        f.write(f"- Final texts: {len(final_cleaned)}\n")
        f.write(f"- Original tokens: {original_tokens}\n")
        f.write(f"- Final tokens: {final_tokens}\n")
        f.write(f"- Removal percentage: {removal_percentage:.2f}%\n")
    
    print("Cleaning complete. Files: clean_corpus.txt, stats.md")
