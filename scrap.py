import sys
import subprocess
import importlib
import re
import time as t
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Auto Install Missing Packages ---
def get_package(*packages):
    for package in packages:
        try:
            importlib.import_module(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        finally:
            globals()[package] = importlib.import_module(package)

# --- Browser Setup ---
def setup_driver(profile_path="C:\\seleniumprofile", profile_dir="Default", driver_path="C:\\seleniumprofile\\chromedriver.exe", headless_mode=False):
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument(f"profile-directory={profile_dir}")
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    if headless_mode:
        options.add_argument('--headless')
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=CSSAnimations,CSSTransitions")

    service = ChromeService(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# --- Simplified Element Lookup ---
def find(driver, method='c', selector=None):
    methods = {
        'c': lambda: driver.find_element(By.CSS_SELECTOR, selector),
        'cm': lambda: driver.find_elements(By.CSS_SELECTOR, selector),
        'x': lambda: driver.find_element(By.XPATH, selector),
        'xm': lambda: driver.find_elements(By.XPATH, selector),
        'n': lambda: driver.find_element(By.NAME, selector),
    }
    return methods.get(method.lower(), lambda: None)()

# --- Job Search URL Constructor ---
def build_jobsearch_url(roles, experience=1, locations=None):
    base_url = 'https://www.naukri.com/'

    role_slug = '-'.join([re.sub(r'\s+', '-', r.strip().lower()) for r in roles]) + "-jobs"
    loc_slug = '-in-' + re.sub(r'\s+', '-', locations[0].strip().lower()) if locations else ''
    query_roles = '%2C%20'.join([r.strip().lower().replace(' ', '%20') for r in roles])
    query_locs = '&l=' + '%2C%20'.join([l.strip().lower().replace(' ', '%20') for l in locations]) if locations else ''

    search_query = f"{query_roles}{query_locs}&experience={experience}&nignbevent_src=jobsearchDeskGNB"
    return f"{base_url}{role_slug}{loc_slug}?k={search_query}"

# --- Scraper Logic ---
def extract_job_data(driver):
    soup = BeautifulSoup(driver.page_source, "lxml")
    cards = soup.select('#listContainer > div > div > div.srp-jobtuple-wrapper > div')
    all_data = []

    for card in cards:
        data = {}
        try:
            a_tag = card.select_one('div.row1 > h2 > a')
            data['title'] = a_tag.text.strip()
            data['jobposting_url'] = a_tag['href']

            try:
                company_tag = card.select_one('div.row2 > span > a')
                data['company_page'] = company_tag['href']
                data['Posted by'] = company_tag.text.strip()
                reviews_available = True
            except:
                fallback = card.select_one('div.row2 > div > a')
                data['company_page'] = fallback['href']
                data['Posted by'] = fallback.text.strip()
                reviews_available = False

            if reviews_available:
                rating = card.select_one('div.row2 > span > a:nth-child(2) > span:nth-child(2)')
                reviews = card.select_one('div.row2 > span > a:nth-child(3)')
                data['rating'] = rating.text if rating else None
                data['no_of_reviews'] = reviews.text.replace('  Reviews', '') if reviews else None
                data['reviews_page_url'] = reviews['href'] if reviews else None
            else:
                data['rating'] = data['no_of_reviews'] = data['reviews_page_url'] = None

            data['experience'] = card.select_one('div.row3 > div.job-details > span.exp-wrap').text.replace(' Yrs', '') if card.select_one('div.row3 > div.job-details > span.exp-wrap') else None

            salary = card.select_one('div.row3 > div.job-details > span.sal-wrap.ver-line > span > span')
            data['salary_offered'] = salary['title'].replace(' Lacs PA', '') if salary else None

            loc = card.select_one('div.row3 > div.job-details > span.loc-wrap.ver-line > span > span')
            data['location(s)'] = loc['title'] if loc else None

            overview = card.select_one('div.row4 > span')
            data['overview_text'] = overview.text.strip() if overview else None

            keywords = [li.text.strip() for li in card.select('div.row5 > ul > li')]
            data['key_words'] = ', '.join(keywords)

            posted = card.select_one('div.row6 > span.job-post-day')
            data['days ago'] = posted.text.strip() if posted else None

            all_data.append(data)

        except Exception as e:
            print(f"[!] Skipping card due to error: {e}")
            continue

    return pd.DataFrame(all_data)

# --- Main Entry Point ---
def main():
    driver = setup_driver()
    driver.get("https://www.naukri.com/mnjuser/homepage")

    url = build_jobsearch_url(['Data Analyst', 'MIS'], experience=1, locations=['Noida'])
    print(f"Navigating to job search URL:\n{url}\n")
    driver.get(url)

    df = extract_job_data(driver)
    df.to_csv("job_data.csv", index=False)
    print("✅ Job data saved to 'job_data.csv'.")

if __name__ == "__main__":
    main()
