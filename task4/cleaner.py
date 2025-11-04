# cleaner.py
# End-to-end cleaner for HW2 Task 4

from __future__ import annotations
import json, re, regex, html, unicodedata, os
from pathlib import Path
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
from datasketch import MinHash, MinHashLSH
from collections import Counter, defaultdict
from unidecode import unidecode
from ftfy import fix_text
from tqdm import tqdm

# ---------- CONFIG ----------
# Adjust these if your folders differ
ROOT = Path(__file__).resolve().parent
TASK1_ARXIV_JSON = ROOT / "arxiv_clean.json"                            # Task 1
TASK2_PDF_TXT_DIR = ROOT.parent / "hw2" / "pdf_ocr"                     # Task 2 (.txt files)
TASK3_TRANSCRIPTS_DIR = ROOT.parent / "hw2" / "transcriptions" / "transcripts"  # Task 3 (.json/.txt)
OUTPUT_CORPUS = ROOT / "clean_corpus.txt"
OUTPUT_STATS = ROOT / "stats.md"
LANG_ALLOW = {"en"}                 # keep English only per assignment (change if needed)
MIN_LEN_CHARS = 300                 # drop super short docs
DEDUP_JACCARD = 0.7                 # MinHash LSH threshold
NGRAM_REPEAT_MAX = 3                # collapse >3 exact repeats
NGRAM_WINDOW = 3                    # n for repeat squashing
# ----------------------------

DetectorFactory.seed = 42

EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"""(?:
    (?:(?:\+?\d{1,3}[\s\-\.])?(?:\(\d{2,4}\)|\d{2,4})[\s\-\.]?)?
    \d{3,4}[\s\-\.]\d{3,4}(?:[\s\-\.]\d{3,4})?
)""", re.VERBOSE)
# 13–19 contiguous digits with optional separators (very rough CC pattern)
CC_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")

HTML_TAG_RE = re.compile(r"<[^>]+>")

def read_task1() -> List[Dict]:
    docs = []
    if TASK1_ARXIV_JSON.exists():
        with open(TASK1_ARXIV_JSON, "r", encoding="utf-8") as f:
            blob = json.load(f)
        # Expect list[ {url,title,abstract,authors,date} ] or similar
        for row in blob:
            text = " ".join(str(row.get(k,"")) for k in ("title","abstract","authors","date","url"))
            docs.append({"source":"task1_arxiv","id":row.get("url") or row.get("id"),"text":text})
    return docs

def read_task2() -> List[Dict]:
    docs = []
    if TASK2_PDF_TXT_DIR.exists():
        for p in TASK2_PDF_TXT_DIR.rglob("*.txt"):
            docs.append({"source":"task2_pdfocr","id":p.stem,"text":p.read_text(encoding="utf-8", errors="ignore")})
    return docs

def read_task3() -> List[Dict]:
    docs = []
    if TASK3_TRANSCRIPTS_DIR.exists():
        for p in TASK3_TRANSCRIPTS_DIR.glob("*.json"):
            try:
                j = json.loads(p.read_text(encoding="utf-8"))
                base = [j.get("title",""), j.get("full_text","")]
                # include OCR text from frames if present
                if j.get("ocr_text"): base.append(j["ocr_text"])
                text = " ".join(base)
                docs.append({"source":"task3_transcript","id":j.get("video_id") or p.stem,"text":text})
            except Exception:
                pass
        # (Optional) also ingest *.txt if you want
        # for p in TASK3_TRANSCRIPTS_DIR.glob("*.txt"):
        #     docs.append({"source":"task3_transcript_txt","id":p.stem,"text":p.read_text(encoding="utf-8", errors="ignore")})
    return docs

def strip_html_noise(s: str) -> str:
    # remove HTML/JS/CSS if any sneaked in
    s = html.unescape(s)
    if "<" in s and ">" in s:
        s = BeautifulSoup(s, "lxml").get_text(separator=" ")
    s = HTML_TAG_RE.sub(" ", s)
    return s

def normalize_text(s: str) -> str:
    s = fix_text(s)
    s = strip_html_noise(s)
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u00AD", "")  # soft hyphen
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    s = s.strip()
    return s

def remove_pii(s: str) -> Tuple[str, Dict[str,int]]:
    counts = {"emails":0,"phones":0,"cards":0}
    s, n1 = EMAIL_RE.subn("[EMAIL]", s)
    s, n2 = PHONE_RE.subn("[PHONE]", s)
    # Avoid trashing years/IDs: mask only if it looks like CC (≥13 digits across separators)
    def _mask_cc(m: re.Match) -> str:
        digits = re.sub(r"\D", "", m.group(0))
        return "[CREDIT_CARD]" if 13 <= len(digits) <= 19 else m.group(0)
    n3 = 0
    out = []
    i = 0
    for m in CC_RE.finditer(s):
        out.append(s[i:m.start()])
        rep = _mask_cc(m)
        if rep == "[CREDIT_CARD]": n3 += 1
        out.append(rep)
        i = m.end()
    out.append(s[i:])
    s = "".join(out)
    counts["emails"], counts["phones"], counts["cards"] = n1, n2, n3
    return s, counts

def squash_repeats(tokens: List[str], n=3, max_repeat=3) -> List[str]:
    """Collapse exact repeated n-grams appearing > max_repeat times consecutively."""
    if len(tokens) < n: return tokens
    out, i = [], 0
    while i <= len(tokens) - n:
        ng = tuple(tokens[i:i+n])
        reps = 1
        j = i + n
        while j <= len(tokens) - n and tuple(tokens[j:j+n]) == ng:
            reps += 1
            j += n
        out.extend(list(ng))
        if reps > max_repeat:
            out.append("[REPEAT]")
        i = j
    # tail
    out.extend(tokens[i:])
    return out

def tokenize_for_shingling(text: str) -> List[str]:
    # lightweight tokenization for both MinHash and repeat squashing
    toks = re.findall(r"[A-Za-z0-9]+", unidecode(text.lower()))
    return toks

def clean_one(text: str) -> Tuple[str, Dict[str,int]]:
    t0 = text
    t = normalize_text(t0)
    t, pii_counts = remove_pii(t)

    # remove very long runs of a single char
    t = regex.sub(r"(\p{L}|\p{N})\1{9,}", r"\1" * 9, t)

    # squash repeated n-grams
    toks = tokenize_for_shingling(t)
    toks = squash_repeats(toks, n=NGRAM_WINDOW, max_repeat=NGRAM_REPEAT_MAX)
    t = " ".join(toks)
    return t, pii_counts

def lang_of(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "unk"

def shingle_set(tokens: List[str], k=5) -> List[str]:
    return [" ".join(tokens[i:i+k]) for i in range(max(0, len(tokens)-k+1))]

def make_minhash(tokens: List[str], k=5, num_perm=128) -> MinHash:
    mh = MinHash(num_perm=num_perm)
    for sh in shingle_set(tokens, k=k):
        mh.update(sh.encode("utf-8"))
    return mh

def main():
    # ------- Load all docs -------
    raw_docs = []
    raw_docs += read_task1()
    raw_docs += read_task2()
    raw_docs += read_task3()

    stats = defaultdict(int)
    pii_totals = Counter()
    kept_docs: List[str] = []
    meta_rows = []

    # ------- Filter by language & length; clean; collect -------
    for d in tqdm(raw_docs, desc="Pre-clean pass"):
        text = d["text"] or ""
        text = normalize_text(text)
        if len(text) < MIN_LEN_CHARS:
            stats["short_dropped"] += 1
            continue
        lang = lang_of(text)
        if LANG_ALLOW and lang not in LANG_ALLOW:
            stats["lang_dropped"] += 1
            continue
        cleaned, pii_counts = clean_one(text)
        if len(cleaned) < MIN_LEN_CHARS:
            stats["cleaned_too_short"] += 1
            continue

        kept_docs.append(cleaned)
        pii_totals.update(pii_counts)
        meta_rows.append({"source": d["source"], "id": d["id"], "lang": lang, "chars": len(cleaned)})

    stats["kept_after_clean"] = len(kept_docs)
    stats["input_docs"] = len(raw_docs)

    # ------- Deduplicate with MinHash LSH -------
    lsh = MinHashLSH(threshold=DEDUP_JACCARD, num_perm=128)
    minh_list = []
    for i, doc in enumerate(kept_docs):
        toks = tokenize_for_shingling(doc)
        mh = make_minhash(toks, k=5, num_perm=128)
        lsh.insert(str(i), mh)
        minh_list.append(mh)

    dup_mark = set()
    for i, mh in enumerate(minh_list):
        if i in dup_mark: 
            continue
        near = lsh.query(mh)
        for j in near:
            j = int(j)
            if j != i:
                dup_mark.add(j)

    dedup_docs = [d for i, d in enumerate(kept_docs) if i not in dup_mark]
    stats["duplicates_removed"] = len(kept_docs) - len(dedup_docs)
    stats["final_docs"] = len(dedup_docs)
    stats["final_chars"] = sum(len(x) for x in dedup_docs)
    stats["pii_email_replacements"] = pii_totals["emails"]
    stats["pii_phone_replacements"] = pii_totals["phones"]
    stats["pii_card_replacements"]  = pii_totals["cards"]

    # ------- Write outputs -------
    OUTPUT_CORPUS.write_text("\n\n==== DOC_SEPARATOR ====\n\n".join(dedup_docs), encoding="utf-8")

    md = []
    md.append("# Cleaning Stats")
    md.append("")
    for k in ["input_docs","kept_after_clean","duplicates_removed","final_docs","final_chars",
              "short_dropped","lang_dropped","cleaned_too_short",
              "pii_email_replacements","pii_phone_replacements","pii_card_replacements"]:
        md.append(f"- **{k.replace('_',' ').title()}**: {stats.get(k,0)}")
    md.append("")
    md.append("## Notes")
    md.append(f"- Language kept: {', '.join(sorted(LANG_ALLOW)) or 'ALL'}")
    md.append(f"- MinHash Jaccard threshold: ≥ {DEDUP_JACCARD}")
    md.append(f"- Repetitive n-gram window: {NGRAM_WINDOW}, collapsed if > {NGRAM_REPEAT_MAX} repeats")
    OUTPUT_STATS.write_text("\n".join(md), encoding="utf-8")

    print(f"\n✓ Wrote {len(dedup_docs)} docs to {OUTPUT_CORPUS}")
    print(f"✓ Stats → {OUTPUT_STATS}")

if __name__ == "__main__":
    main()
