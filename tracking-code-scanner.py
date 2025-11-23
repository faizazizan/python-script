import requests, re

# === Regex pattern senarai tracking code ===
patterns = {
    "Google Tag Manager": r"(GTM-[A-Z0-9]+)",
    "Google Analytics 4 (GA4)": r"(G-[A-Z0-9]+)",
    "Google Analytics (UA)": r"(UA-\d{4,10}-\d+)",
    "Meta Pixel": r"fbq\('init',\s*['\"]?(\d+)['\"]?\)",
    "TikTok Pixel": r"ttq\.load\(['\"]?(\d+)['\"]?\)",
    "LinkedIn Insight Tag": r"linkedin\.com/li\.js",
    "Twitter Pixel": r"static\.ads-twitter\.com",
    "Google Ads Remarketing": r"AW-(\d+)",
    "Google Search Console": r"google-site-verification[\"']?\s*content=[\"'](.*?)['\"]"
}

# === Tentukan origin berdasarkan konteks ===
def detect_origin(line):
    if "googletagmanager" in line:
        return "Origin: GTM"
    elif "plugin" in line or "wp-content/plugins" in line:
        return "Origin: Plugin"
    else:
        return "Origin: Hardcoded"

# === Fungsi utama untuk scan ===
def detect_tracking(url):
    if not url.startswith("http"):
        url = "https://" + url.strip()
    print(f"\n🔍 Scanning {url} ...\n")

    try:
        response = requests.get(url, timeout=10)
        html = response.text

        results = {}
        for name, pattern in patterns.items():
            matches = re.findall(pattern, html)
            if matches:
                # Cari line yang mengandungi match → kesan origin
                for match in matches:
                    match_line = next((l for l in html.splitlines() if match in l), "")
                    origin = detect_origin(match_line)
                    results[name] = f"✅ {', '.join(matches)} ({origin})"
            else:
                results[name] = "❌"

        # Detect dataLayer.push event
        events = re.findall(r"dataLayer\.push\((.*?)\)", html)
        if events:
            results["Event Push Found"] = f"✅ {len(events)} event(s) found"
            results["Sample Events"] = events[:3]
        else:
            results["Event Push Found"] = "❌"

        return results

    except Exception as e:
        return {"Error": str(e)}

# === Main Execution ===
if __name__ == "__main__":
    website = input("🌐 Masukkan URL website: ")
    result = detect_tracking(website)

    print("\n📊 Tracking Results:\n")
    for key, value in result.items():
        print(f"{key}: {value}")
