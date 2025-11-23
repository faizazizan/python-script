mport requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import pipeline

# ✅ Senarai URL (boleh baca dari CSV / sitemap juga)
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
]

# Init dataframe
data = []

# ✅ Scrape semua URL
for url in urls:
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        images = soup.find_all("img")

        for img in images:
            src = img.get("src")
            alt = img.get("alt", "")
            if src:
                data.append({
                    "page_url": url,
                    "image_url": src,
                    "alt_original": alt
                })
    except Exception as e:
        print(f"Error scraping {url}: {e}")

df = pd.DataFrame(data)

# ✅ Setup LLM pipeline
generator = pipeline("text2text-generation", model="facebook/bart-large-cnn")

def rewrite_alt(alt_text):
    if not alt_text.strip():
        return ""
    try:
        result = generator(
            f"Rewrite this alt text to be SEO-friendly and descriptive: {alt_text}",
            max_length=30,
            do_sample=False
        )
        return result[0]['generated_text']
    except:
        return alt_text

# ✅ Rewrite bulk alt
df["alt_rewritten"] = df["alt_original"].apply(rewrite_alt)

# ✅ Save ke CSV
df.to_csv("bulk_rewritten_alts.csv", index=False, encoding="utf-8")

print("✅ Done! CSV saved as bulk_rewritten_alts.csv")
