from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import time
import random
import pandas as pd

# Replace with your Instagram login credentials
USERNAME = "your-username"
PASSWORD = "your-password"

# Target Instagram profile
TARGET_PROFILE = "https://www.instagram.com/username/"

def human_delay(a=2, b=4):
    """Sleep with random delay to simulate human behavior."""
    time.sleep(random.uniform(a, b))

def dismiss_popups(driver):
    """Dismiss Instagram's 'Save Info' and 'Turn on Notifications' popups."""
    try:
        # Save Your Login Info?
        not_now_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Not Now"]'))
        )
        not_now_btn.click()
        human_delay()
    except:
        pass

    try:
        # Turn on Notifications?
        not_now_btn2 = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Not Now"]'))
        )
        not_now_btn2.click()
        human_delay()
    except:
        pass

def login(driver):
    """Logs into Instagram."""
    driver.get("https://www.instagram.com/accounts/login/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    human_delay(5, 7)
    dismiss_popups(driver)

def scroll_and_collect_post_links(driver, max_scrolls=10):
    """Scrolls and collects post URLs from the profile page."""
    driver.get(TARGET_PROFILE)
    human_delay(5, 6)

    post_links = set()
    for _ in range(max_scrolls):
        anchors = driver.find_elements(By.TAG_NAME, "a")
        for a in anchors:
            href = a.get_attribute("href")
            if href and "/p/" in href:
                post_links.add(href)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_delay(3, 5)
    return list(post_links)

def extract_post_data(driver, url):
    """Extracts caption and media URL from a post."""
    driver.get(url)
    human_delay(3, 4)

    data = {
        "post_url": url,
        "media_url": "",
        "caption": ""
    }

    try:
        caption_elem = driver.find_element(By.XPATH, '//div[@role="dialog"]//span')
        data["caption"] = caption_elem.text
    except:
        try:
            caption_elem = driver.find_element(By.XPATH, '//div[@class="_a9zs"]')
            data["caption"] = caption_elem.text
        except:
            data["caption"] = ""

    try:
        img = driver.find_element(By.XPATH, '//img[@decoding="auto"]')
        data["media_url"] = img.get_attribute("src")
    except:
        try:
            video = driver.find_element(By.TAG_NAME, "video")
            data["media_url"] = video.get_attribute("src")
        except:
            data["media_url"] = ""

    return data

def main():
    options = Options()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Optional

    driver = webdriver.Chrome(options=options)

    # Stealth mode
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    try:
        login(driver)
        post_urls = scroll_and_collect_post_links(driver, max_scrolls=8)

        all_data = []
        for idx, post_url in enumerate(post_urls):
            print(f"[{idx+1}/{len(post_urls)}] Scraping: {post_url}")
            post_data = extract_post_data(driver, post_url)
            all_data.append(post_data)

        # Save to CSV
        df = pd.DataFrame(all_data)
        df.to_csv("instagram_data.csv", index=False)
        print("✅ Data saved to instagram_data.csv")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
