import os
import re
import json
import glob
import html
from langdetect import detect
from datasketch import MinHash, MinHashLSH
from tqdm import tqdm

# -------------------- Configuration --------------------
ARXIV_JSON = r"D:\MLE\Homework2-Submission\arxiv_clean.json"
OCR_FOLDER = r"D:\MLE\Homework2-Submission\pdf_ocr"
ASR_FILE = r"D:\MLE\Homework2-Submission\outputs\talks_transcripts.jsonl"

OUTPUT_TEXT = r"D:\MLE\Homework2-Submission\clean_corpus.txt"
OUTPUT_STATS = r"D:\MLE\Homework2-Submission\stats.md"

SIMILARITY_THRESHOLD = 0.7
MINHASH_SEED = 42

# -------------------- Functions --------------------
def clean_text(text):
    """Remove HTML, Markdown, and special symbols"""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def is_english(text):
    """Detect whether the text is English or a mix of Chinese and English"""
    try:
        lang = detect(text)
        return lang in ["en", "zh-cn", "zh-tw"]
    except:
        return False

def remove_pii(text):
    """Remove personally identifiable information"""
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[EMAIL]", text)
    text = re.sub(r"\b(?:\d[ -]*?){13,16}\b", "[CREDIT_CARD]", text)
    text = re.sub(r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b", "[PHONE]", text)
    return text

def remove_repetitive_ngrams(text):
    """Remove repetitive short phrases"""
    tokens = text.split()
    result = []
    for i, token in enumerate(tokens):
        if i > 0 and token == tokens[i - 1]:
            continue
        result.append(token)
    return " ".join(result)

def text_to_minhash(text):
    """Convert text to a MinHash signature"""
    m = MinHash(num_perm=128, seed=MINHASH_SEED)
    for word in set(text.split()):
        m.update(word.encode('utf8'))
    return m

# -------------------- Main Process --------------------
def main():
    all_texts = []

    # 1️⃣ Read arxiv_clean.json
    if os.path.exists(ARXIV_JSON):
        with open(ARXIV_JSON, "r", encoding="utf-8") as f:
            papers = json.load(f)
        for p in papers:
            txt = clean_text(p.get("title", "") + " " + p.get("abstract", ""))
            if is_english(txt):
                all_texts.append(txt)

    # 2️⃣ Read OCR text files
    if os.path.isdir(OCR_FOLDER):
        for file in glob.glob(os.path.join(OCR_FOLDER, "*.txt")):
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                txt = clean_text(f.read())
                if is_english(txt):
                    all_texts.append(txt)

    # 3️⃣ Read ASR transcripts
    if os.path.exists(ASR_FILE):
        with open(ASR_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    txt = clean_text(data.get("text", ""))
                    if is_english(txt):
                        all_texts.append(txt)
                except:
                    continue

    print(f"📄 Combined total: {len(all_texts)} documents")

    # 4️⃣ Clean PII and repetitive n-grams
    cleaned_texts = []
    for t in tqdm(all_texts, desc="Cleaning texts"):
        t = remove_pii(remove_repetitive_ngrams(t))
        cleaned_texts.append(t)

    # 5️⃣ Deduplication (MinHash)
    lsh = MinHashLSH(threshold=SIMILARITY_THRESHOLD, num_perm=128)
    unique_texts = []
    for i, t in enumerate(tqdm(cleaned_texts, desc="Deduplicating")):
        m = text_to_minhash(t)
        if len(lsh.query(m)) == 0:
            lsh.insert(str(i), m)
            unique_texts.append(t)

    # 6️⃣ Output cleaned corpus
    print(f"📝 Writing to {OUTPUT_TEXT} ...")
    os.makedirs(os.path.dirname(OUTPUT_TEXT), exist_ok=True)
    with open(OUTPUT_TEXT, "w", encoding="utf-8") as f:
        for t in unique_texts:
            f.write(t + "\n\n")

    # 7️⃣ Generate statistics report
    print(f"📊 Writing statistics report to {OUTPUT_STATS} ...")
    removed = len(all_texts) - len(unique_texts)
    total_tokens = sum(len(t.split()) for t in unique_texts)
    with open(OUTPUT_STATS, "w", encoding="utf-8") as f:
        f.write(f"# Cleaning Summary\n")
        f.write(f"- Total documents before cleaning: {len(all_texts)}\n")
        f.write(f"- After deduplication: {len(unique_texts)}\n")
        f.write(f"- Removed duplicates: {removed}\n")
        f.write(f"- Total tokens: {total_tokens}\n")

    print(f"\n✅ Cleaning complete: {len(unique_texts)} documents written to {OUTPUT_TEXT}")
    print(f"📊 Statistics saved to {OUTPUT_STATS}")

# -------------------- Entry Point --------------------
if __name__ == "__main__":
    main()
