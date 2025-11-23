from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# === SETTINGS ===
MAPS_URL = "https://www.google.com/maps/your-business-map-id"

# === SETUP SELENIUM ===
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get(MAPS_URL)
time.sleep(5)

# === CLICK "All reviews" BUTTON ===
try:
    all_reviews_button = driver.find_element(By.XPATH, "//button[contains(@aria-label,'Reviews')]")
    driver.execute_script("arguments[0].click();", all_reviews_button)
    print("🖱️ Clicked 'All reviews' button")
except Exception as e:
    print("⚠️ Could not find 'All reviews' button:", e)

time.sleep(5)

# === SCROLL UNTIL NO MORE REVIEWS ===
scrollable_div = driver.find_element(By.XPATH, "//div[contains(@class, 'm6QErb DxyBCb kA9KIf dS8AEf')]")
previous_height = 0
scroll_round = 0

while True:
    driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight);', scrollable_div)
    time.sleep(2)
    new_height = driver.execute_script('return arguments[0].scrollHeight;', scrollable_div)
    scroll_round += 1
    print(f"  ⏳ Scroll pass {scroll_round}...")
    if new_height == previous_height:
        print("✅ Reached end of reviews.")
        break
    previous_height = new_height

# === GET ALL REVIEW TEXTS ===
reviews = driver.find_elements(By.XPATH, "//div[@class='MyEned']")

data = []
for idx, review in enumerate(reviews, start=1):
    try:
        text = review.text.strip()
        if text:
            data.append({"index": idx, "review": text})
    except Exception:
        continue

print(f"📊 Total reviews extracted: {len(data)}")

# === SAVE TO CSV ===
df = pd.DataFrame(data)
df.to_csv("google_reviews_text_only.csv", index=False, encoding="utf-8-sig")
print("✅ Saved to 'google_reviews_text_only.csv'")

driver.quit()
