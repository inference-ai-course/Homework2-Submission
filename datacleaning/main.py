#!/usr/bin/env python3
import argparse
import os
import re
import json
import glob
import html
import nltk 
from typing import Iterable, List, Dict, Any, Tuple, Optional
from bs4 import BeautifulSoup  # type: ignore
from nltk.tokenize import wordpunct_tokenize

# Language detection
from langdetect import detect, DetectorFactory  # type: ignore

# Dedupe via datasketch
from datasketch import MinHash, MinHashLSH  # type: ignore

DetectorFactory.seed = 0  # make detection deterministic

def read_text_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return [{"source_file": os.path.basename(path), "text": text}]


def _extract_texts_from_json_obj(obj: Any, collected: List[str]) -> None:
    if obj is None:
        return
    if isinstance(obj, str):
        s = obj.strip()
        if s:
            collected.append(s)
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            # Heuristic: prefer typical text-bearing fields
            if isinstance(v, str) and k.lower() in {
                "title", "summary", "abstract", "content", "text", "body", "description"
            }:
                s = v.strip()
                if s:
                    collected.append(s)
            else:
                _extract_texts_from_json_obj(v, collected)
        return
    if isinstance(obj, (list, tuple)):
        for it in obj:
            _extract_texts_from_json_obj(it, collected)
        return
    # ignore other types


def read_json_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            # fallback: attempt JSON lines
            f.seek(0)
            items = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except Exception:
                    pass
            data = items

    records: List[Dict[str, Any]] = []
    if isinstance(data, list):
        iterable = data
    else:
        iterable = [data]

    for item in iterable:
        texts: List[str] = []
        _extract_texts_from_json_obj(item, texts)
        combined = "\n\n".join(t for t in texts if t)
        if combined.strip():
            records.append({
                "source_file": os.path.basename(path),
                "text": combined
            })
    return records


def strip_html_and_redact_pii(text: str) -> str:
    if not text:
        return text
    soup = BeautifulSoup(text, "lxml")

    # Remove non-visible/unsafe content
    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()

    # Redact mailto/tel and drop tracking params
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if isinstance(href, str):
            href_lower = href.lower()
            if href_lower.startswith("mailto:"):
                a.string = "[EMAIL]"
                a.attrs.pop("href", None)
            elif href_lower.startswith("tel:"):
                a.string = "[PHONE]"
                a.attrs.pop("href", None)
            else:
                # Strip obvious PII in query strings (best-effort)
                a.attrs.pop("href", None)

    # Remove elements that likely contain PII by id/class/itemprop/name hints
    pii_hint_re = re.compile(r"(email|e-?mail|contact|phone|tel|author|name|address)", re.IGNORECASE)
    for el in soup.find_all(True):
        attrs_text = " ".join(
            [el.get("id", ""), " ".join(el.get("class", [])), el.get("itemprop", ""), el.get("name", "")]
            if isinstance(el.get("class", []), list) else [el.get("id", ""), el.get("class", ""), el.get("itemprop", ""), el.get("name", "")]
        )
        if attrs_text and pii_hint_re.search(attrs_text):
            el.decompose()

    # Extract visible text and unescape entities
    plain = soup.get_text(separator=" ", strip=True)
    return html.unescape(plain)
    
def normalize_ws(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", " ", text).strip()


def detect_language(text: str) -> Optional[str]:
    try:
        return detect(text)
    except Exception:
        return None


def tokenize_words(text: str) -> List[str]:
    toks = wordpunct_tokenize(text)
    toks = [t.lower() for t in toks if re.search(r"[A-Za-z0-9]", t)]
    return toks


def remove_repetitive_ngrams(text: str, min_n: int = 3, max_n: int = 6) -> str:
    tokens = tokenize_words(text)
    if not tokens:
        return text

    # Remove consecutive repeated n-grams
    i = 0
    kept = []
    while i < len(tokens):
        repeated = False
        for n in range(max_n, min_n - 1, -1):
            if i + 2 * n <= len(tokens):
                a = tokens[i:i + n]
                b = tokens[i + n:i + 2 * n]
                if a == b:
                    kept.extend(a)  # keep one occurrence
                    i += n  # skip only one repetition
                    repeated = True
                    break
        if not repeated:
            kept.append(tokens[i])
            i += 1

    # Optionally, drop globally over-repeated n-grams (retain first occurrence)
    for n in range(min_n, max_n + 1):
        seen = set()
        j = 0
        while j <= len(kept) - n:
            tup = tuple(kept[j:j + n])
            if tup in seen:
                # Remove subsequent duplicates; do not insert placeholder to avoid OOB
                del kept[j:j + n]
                # do not advance j so we can check for further repeats at the same index
            else:
                seen.add(tup)
                j += 1

    return " ".join(kept)


def shingles(tokens: List[str], n: int = 3) -> List[str]:
    if len(tokens) < n:
        return [" ".join(tokens)] if tokens else []
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def text_to_minhash(text: str, num_perm: int = 128, shingle_n: int = 3) -> Tuple[MinHash, set]:
    toks = tokenize_words(text)
    sh = set(shingles(toks, n=shingle_n)) if toks else set()
    mh = MinHash(num_perm=num_perm)
    if sh:
        for s in sh:
            mh.update(s.encode("utf-8"))
    else:
        mh.update(b"")  # ensure non-empty
    return mh, sh


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def collect_input_records(input_dir: str) -> List[Dict[str, Any]]:
    paths = []
    paths.extend(glob.glob(os.path.join(input_dir, "*.txt")))
    paths.extend(glob.glob(os.path.join(input_dir, "*.json")))
    records: List[Dict[str, Any]] = []
    for p in sorted(set(paths)):
        ext = os.path.splitext(p)[1].lower()
        try:
            if ext == ".txt":
                records.extend(read_text_file(p))
            elif ext == ".json":
                records.extend(read_json_file(p))
        except Exception as e:
            print(f"Skipping {p}: {e}")
    return records


def clean_text_pipeline(text: str) -> str:
    t = strip_html_and_redact_pii(text)
    t = normalize_ws(t)
    t = remove_repetitive_ngrams(t, min_n=3, max_n=6)
    t = normalize_ws(t)
    return t


def deduplicate(records: List[Dict[str, Any]],
                threshold: float = 0.7,
                num_perm: int = 128,
                shingle_n: int = 3) -> List[Dict[str, Any]]:
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    kept: List[Dict[str, Any]] = []
    signatures: List[Tuple[MinHash, set]] = []

    for idx, rec in enumerate(records):
        mh, sh = text_to_minhash(rec["text"], num_perm=num_perm, shingle_n=shingle_n)
        # Query candidates
        candidates = lsh.query(mh)
        is_dup = False
        if candidates:
            # Verify using exact Jaccard on shingles
            for cand in candidates:
                c_mh, c_sh = signatures[cand]  # type: ignore[index]
                sim = jaccard(sh, c_sh)
                if sim >= threshold:
                    is_dup = True
                    break
        if not is_dup:
            lsh.insert(len(signatures), mh)
            signatures.append((mh, sh))
            kept.append(rec)
    return kept


def main():
    parser = argparse.ArgumentParser(description="Clean, deduplicate, and combine input data.")
    parser.add_argument("--input", default=os.path.join(os.path.dirname(__file__), "input"),
                        help="Input directory containing .txt and .json files.")
    parser.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "output.txt"),
                        help="Output file path (JSONL if ends with .jsonl, else plain text).")
    parser.add_argument("--threshold", type=float, default=0.7, help="Similarity threshold for deduplication.")
    parser.add_argument("--shingle_n", type=int, default=3, help="Word shingle size for MinHash/Jaccard.")
    parser.add_argument("--num_perm", type=int, default=128, help="Number of permutations for MinHash.")
    parser.add_argument("--lang", default=None, help="If set (e.g., 'en'), keep only records with detected language.")
    args = parser.parse_args()

    input_dir = args.input
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    raw_records = collect_input_records(input_dir)

    cleaned: List[Dict[str, Any]] = []
    for rec in raw_records:
        text = rec.get("text", "")
        if not text or not text.strip():
            continue
        t = clean_text_pipeline(text)
        if not t:
            continue
        lang = detect_language(t) or ""
        if args.lang and lang != args.lang:
            continue
        cleaned.append({
            "source_file": rec.get("source_file", ""),
            "lang": lang,
            "text": t
        })

    deduped = deduplicate(cleaned, threshold=args.threshold, num_perm=args.num_perm, shingle_n=args.shingle_n)

    # Write output
    if args.out.lower().endswith(".jsonl"):
        with open(args.out, "w", encoding="utf-8") as f:
            for i, rec in enumerate(deduped):
                obj = {
                    "id": i,
                    "source_file": rec["source_file"],
                    "lang": rec.get("lang", ""),
                    "text": rec["text"],
                }
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            for i, rec in enumerate(deduped):
                header = f"### id={i} source={rec['source_file']} lang={rec.get('lang','')}"
                f.write(header + "\n")
                f.write(rec["text"] + "\n\n")

    print(f"Collected: {len(raw_records)} | Cleaned: {len(cleaned)} | Deduplicated: {len(deduped)}")
    print(f"Wrote: {args.out}")


if __name__ == "__main__":
    main()