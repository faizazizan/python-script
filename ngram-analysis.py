#!/usr/bin/env python3
"""
scrape_competitors.py
- Fetch top-N search results (SerpAPI or Bing fallback)
- Fetch each page HTML, extract H1-H6 and visible text
- Compute TF-IDF top n-grams (1-3)
- Save CSV/Excel + per-page report

Usage examples:
  python scrape_competitors.py --keyword "best running shoes" --topn 3 --outdir results
  python scrape_competitors.py --urls urls.txt --outdir results
"""
import argparse
import time
import json
import os
import re
from collections import Counter
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import tldextract

# ---------- CONFIG ----------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}
REQUEST_TIMEOUT = 15
RETRY_COUNT = 2
SLEEP_BETWEEN = 1.0
# ----------------------------

# Basic stopword set (extend if needed)
STOPWORDS = set("a an the of in on for to with by from is are as that this it be or at which and or".split())

def safe_get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, retries=RETRY_COUNT):
    """Fetch URL with retries and basic error handling."""
    for attempt in range(retries+1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return resp.text
            else:
                # non-200: break or retry small number
                print(f"[warn] {url} returned {resp.status_code}")
        except Exception as e:
            print(f"[error] fetching {url} attempt {attempt}: {e}")
        time.sleep(1 + attempt * 0.5)
    return ""

def clean_text_from_html(html: str) -> str:
    """Extract visible text and collapse whitespace."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    for s in soup(["script", "style", "noscript", "svg", "iframe"]):
        s.decompose()
    text = soup.get_text(separator=" ")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_headings(html: str, levels=("h1","h2","h3","h4","h5","h6")) -> List[Tuple[str,str]]:
    """Return list of (tag, text) in document order."""
    soup = BeautifulSoup(html, "lxml")
    headings = []
    for el in soup.find_all(re.compile("^h[1-6]$")):
        if el.name in levels:
            txt = el.get_text(separator=" ").strip()
            if txt:
                headings.append((el.name, txt))
    return headings

def tokenize(text: str):
    tokens = re.findall(r"[a-zA-Z0-9']{2,}", text.lower())
    tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens

def ngrams_from_tokens(tokens, n):
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def top_ngrams_for_text(text, topk=30, ngram_range=(1,3)):
    tokens = tokenize(text)
    c = Counter()
    for n in range(ngram_range[0], ngram_range[1]+1):
        c.update(ngrams_from_tokens(tokens, n))
    return c.most_common(topk)

# ---------- SERP helpers ----------
def serpapi_search(keyword: str, serpapi_key: str, topn: int = 3) -> List[str]:
    """Return list of topn result urls using SerpAPI (if available)."""
    try:
        from google_search_results import GoogleSearch
    except Exception:
        print("[serpapi] google-search-results library not installed.")
        return []
    params = {"q": keyword, "engine": "google", "num": topn, "api_key": serpapi_key}
    gs = GoogleSearch(params)
    results = gs.get_dict()
    urls = []
    for r in results.get("organic_results", [])[:topn]:
        link = r.get("link")
        if link:
            urls.append(link)
    return urls

def bing_search_scrape(keyword: str, topn: int = 3) -> List[str]:
    """Fallback: scrape Bing search results (simple)."""
    q = requests.utils.requote_uri(keyword)
    url = f"https://www.bing.com/search?q={q}&count={topn}"
    html = safe_get(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    urls = []
    for li in soup.select("li.b_algo h2 a")[:topn]:
        href = li.get("href")
        if href:
            urls.append(href)
    return urls

# ---------- Main pipeline ----------
def analyze_pages(urls: List[str], outdir: str, ngram_range=(1,3), topk=30):
    os.makedirs(outdir, exist_ok=True)
    page_texts = []
    meta = []
    headings_collection = []

    for idx, url in enumerate(urls, start=1):
        print(f"[fetch] ({idx}/{len(urls)}) {url}")
        html = safe_get(url)
        time.sleep(SLEEP_BETWEEN)
        text = clean_text_from_html(html)
        page_texts.append(text)
        headings = extract_headings(html)
        headings_collection.append(headings)
        domain = tldextract.extract(url).fqdn
        meta.append({"url": url, "domain": domain, "text_len": len(text), "headings_count": len(headings)})
        # Save raw HTML & headings
        with open(os.path.join(outdir, f"page_{idx}.html"), "w", encoding="utf-8") as f:
            f.write(html)
        with open(os.path.join(outdir, f"page_{idx}_headings.json"), "w", encoding="utf-8") as f:
            json.dump(headings, f, ensure_ascii=False, indent=2)

    # TF-IDF across pages
    vectorizer = TfidfVectorizer(ngram_range=ngram_range, analyzer='word', token_pattern=r"[a-zA-Z0-9']{2,}")
    try:
        X = vectorizer.fit_transform(page_texts)
    except ValueError:
        print("[error] TF-IDF failed (maybe empty texts).")
        X = None

    feature_names = vectorizer.get_feature_names_out() if X is not None else []
    top_ngrams_per_page = []
    for i in range(len(urls)):
        row = {}
        if X is not None:
            arr = X[i].toarray().ravel()
            top_idx = arr.argsort()[::-1][:topk]
            top_terms = [(feature_names[j], float(arr[j])) for j in top_idx if arr[j] > 0]
        else:
            top_terms = top_ngrams_for_text(page_texts[i], topk=topk, ngram_range=ngram_range)
        row["url"] = urls[i]
        row["top_ngrams"] = top_terms
        top_ngrams_per_page.append(row)

    # Headings TF-IDF (combine headings per page)
    heading_texts = [" ".join([h[1] for h in hs]) for hs in headings_collection]
    heading_tfidf = None
    if any(heading_texts):
        hv = TfidfVectorizer(ngram_range=(1,2), token_pattern=r"[a-zA-Z0-9']{2,}")
        try:
            HX = hv.fit_transform(heading_texts)
            h_features = hv.get_feature_names_out()
            heading_top = []
            for i in range(HX.shape[0]):
                arr = HX[i].toarray().ravel()
                top_idx = arr.argsort()[::-1][:20]
                top = [(h_features[j], float(arr[j])) for j in top_idx if arr[j] > 0]
                heading_top.append(top)
            heading_tfidf = heading_top
        except Exception:
            heading_tfidf = [top_ngrams_for_text(ht, topk=10, ngram_range=(1,2)) for ht in heading_texts]
    else:
        heading_tfidf = [[] for _ in urls]

    # Write results
    rows = []
    for i, u in enumerate(urls):
        top = top_ngrams_per_page[i]["top_ngrams"]
        head_top = heading_tfidf[i] if i < len(heading_tfidf) else []
        # flatten top terms to columns
        row = {"url": u, "domain": meta[i]["domain"], "text_len": meta[i]["text_len"], "headings_count": meta[i]["headings_count"]}
        for j, (ng,score) in enumerate(top[:20], start=1):
            row[f"ngram_{j}"] = f"{ng} ({score:.4f})"
        row["head_top"] = json.dumps(head_top, ensure_ascii=False)
        rows.append(row)

        # Per-page report (simple)
        rpt_lines = []
        rpt_lines.append(f"URL: {u}")
        rpt_lines.append(f"Domain: {meta[i]['domain']}")
        rpt_lines.append(f"Text length: {meta[i]['text_len']}")
        rpt_lines.append(f"Headings count: {meta[i]['headings_count']}\n")
        rpt_lines.append("Headings:")
        for htag, htxt in headings_collection[i]:
            rpt_lines.append(f"  {htag.upper()}: {htxt}")
        rpt_lines.append("\nTop n-grams (TF-IDF):")
        for ng,score in top[:20]:
            rpt_lines.append(f"  {ng} — {score:.4f}")
        rpt_text = "\n".join(rpt_lines)
        with open(os.path.join(outdir, f"page_{i+1}_report.txt"), "w", encoding="utf-8") as f:
            f.write(rpt_text)

    df = pd.DataFrame(rows)
    csv_path = os.path.join(outdir, "competitor_ngrams.csv")
    df.to_csv(csv_path, index=False)
    excel_path = os.path.join(outdir, "competitor_ngrams.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"[done] CSV saved: {csv_path}")
    print(f"[done] Excel saved: {excel_path}")

    return df

# ---------- CLI ----------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--keyword", help="Keyword to search (gets topN SERP results)")
    p.add_argument("--serpapi_key", help="SerpAPI key (optional)")
    p.add_argument("--topn", type=int, default=3, help="Top N results per keyword")
    p.add_argument("--urls", help="Path to file containing list of URLs (one per line). If provided, will skip search.")
    p.add_argument("--outdir", default="results", help="Output directory")
    p.add_argument("--ngram_min", type=int, default=1)
    p.add_argument("--ngram_max", type=int, default=3)
    args = p.parse_args()

    urls = []
    if args.urls:
        if not os.path.exists(args.urls):
            print("[error] URLs file not found.")
            return
        with open(args.urls, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    elif args.keyword:
        # try serpapi first
        if args.serpapi_key:
            print("[info] Searching via SerpAPI...")
            try:
                urls = serpapi_search(args.keyword, args.serpapi_key, topn=args.topn)
            except Exception as e:
                print("[serpapi] failed:", e)
                urls = []
        if not urls:
            print("[info] Using Bing scraping fallback...")
            urls = bing_search_scrape(args.keyword, topn=args.topn)
    else:
        print("Provide --keyword or --urls")
        return

    if not urls:
        print("[error] No URLs found to analyze.")
        return

    print(f"[info] Found {len(urls)} URLs. Starting analysis...")
    analyze_pages(urls, args.outdir, ngram_range=(args.ngram_min, args.ngram_max))

if __name__ == "__main__":
    main()
