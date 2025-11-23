import requests
from PIL import Image
from io import BytesIO
import os
import re
from urllib.parse import urlparse

# ===== CONFIG =====
output_folder = "folder-name"
urls = [
    "https://your-url.com/wp-content/uploads/",
    "https://your-url.com/",
  
]

# Make output folder
os.makedirs(output_folder, exist_ok=True)

def safe_filename(url):
    """Extract filename safely from URL and append .webp"""
    path = urlparse(url).path
    filename = os.path.basename(path)
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)  # clean
    return filename + ".webp"  # keep original + add .webp

# Download & convert
for i, url in enumerate(urls, 1):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()

        if url.lower().endswith(".svg"):
            print(f"[{i}] Skipped SVG (not supported by Pillow): {url}")
            continue

        img = Image.open(BytesIO(r.content))
        output_path = os.path.join(output_folder, safe_filename(url))

        img.save(output_path, "WEBP", quality=90)
        print(f"[{i}] Saved {output_path}")

    except Exception as e:
        print(f"[{i}] Failed {url}: {e}")
