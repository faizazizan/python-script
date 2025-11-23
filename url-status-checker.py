import requests
import pandas as pd
from tqdm import tqdm
import os

# === SETTING FILE PATH ===
input_file = r"C:\xxxx.csv"
output_file = os.path.join(os.path.dirname(input_file), "url_check_results.csv")

# === BACA CSV ===
df = pd.read_csv(input_file)

# Cuba detect column yang ada URL
colname = None
for c in df.columns:
    if c.lower() in ["url", "urls", "link", "links", "website", "page"]:
        colname = c
        break

if not colname:
    raise ValueError("❌ Tiada column bernama 'url', 'link', atau 'website' dalam CSV!")

urls = df[colname].dropna().tolist()
results = []

# === CHECK URL SATU-SATU ===
for url in tqdm(urls, desc="Checking URLs"):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        code = response.status_code
        if code == 200:
            status = "✅ Valid"
        elif code == 404:
            status = "❌ 404 Not Found"
        else:
            status = f"⚠️ {code}"
    except requests.exceptions.RequestException:
        code = "Error"
        status = "⚠️ Invalid / Timeout"
    results.append({"URL": url, "Status Code": code, "Status": status})

# === SIMPAN KE CSV ===
out_df = pd.DataFrame(results)
out_df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\n✅ Selesai! Hasil disimpan ke:\n{output_file}")
