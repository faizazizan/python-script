import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

TARGET_PROFILE = "https://www.tiktok.com/@xx"

def scroll_and_collect_video_links(driver, max_scrolls=50):
    driver.get(TARGET_PROFILE)
    time.sleep(5)

    video_links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(max_scrolls):
        anchors = driver.find_elements(By.TAG_NAME, "a")
        for a in anchors:
            href = a.get_attribute("href")
            if href and "/video/" in href:
                video_links.add(href)

        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(3)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print(f"✅ Reached bottom at scroll #{i}")
            break
        last_height = new_height

    print(f"🎯 Collected {len(video_links)} video links.")
    return list(video_links)

def extract_video_data(driver, url):
    driver.get(url)
    time.sleep(5)

    data = {
        "post_url": url,
        "media_url": "",
        "caption": ""
    }

    try:
        # Caption
        caption_elem = driver.find_element(By.XPATH, '//h1')
        data["caption"] = caption_elem.text
    except:
        data["caption"] = ""

    try:
        video = driver.find_element(By.TAG_NAME, 'video')
        data["media_url"] = video.get_attribute("src")
    except:
        data["media_url"] = ""

    return data

def main():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    try:
        video_urls = scroll_and_collect_video_links(driver, max_scrolls=60)

        all_data = []
        for idx, url in enumerate(video_urls):
            print(f"[{idx+1}/{len(video_urls)}] Scraping: {url}")
            data = extract_video_data(driver, url)
            all_data.append(data)

        df = pd.DataFrame(all_data)
        df.to_csv("tiktok_data.csv", index=False)
        print("✅ Data saved to tiktok_data.csv")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
