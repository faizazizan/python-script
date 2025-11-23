import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Target URL
url = "https://yourweb.com"
domain = urlparse(url).netloc

# Fetch webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Extract image URLs only from the same domain
img_urls = []
for img in soup.find_all("img"):
    src = img.get("src")
    if src:
        src = urljoin(url, src)  # Convert relative URLs to absolute
        # Keep only images from the same domain
        if urlparse(src).netloc == domain:
            img_urls.append(src)

# Print all image URLs
for i, img_url in enumerate(img_urls, 1):
    print(f"{i}: {img_url}")

print(f"\nTotal images found from {domain}: {len(img_urls)}")
