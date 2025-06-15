import sys
import subprocess
import importlib
import time as t
def get_package(*packages):
    for package_name in packages:
        try:
            importlib.import_module(package_name)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        finally:
            globals()[package_name] = importlib.import_module(package_name)
from selenium import webdriver
profile_data = [r"c:\seleniumprofile","Default"]

# for the seleium profile, it has to be cloned from the path of the user_data of the chrome browser
# the path has to be cloned on c:\seleniumprofile
# before that selenium profile directory has to be created
driver_path = r"C:\seleniumprofile\chromedriver.exe"

# the chrome has to be downloaded on a standard directory, and it shall be within seleniumprofile 

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as chromeservice

options = webdriver.ChromeOptions()
# makes 
options.add_argument(rf"user-data-dir={profile_data[0]}")
options.add_argument(rf"profile-directory={profile_data[1]}")

# function for making the browser headless and is supposed be executed before initialising the browser
def headless():
    options.add_argument('--headless')
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=CSSAnimations,CSSTransitions")
# detaches the browser's instance dependency on code execution, and makes the window standalone
options.add_experimental_option("detach", True)
# removes the "this window is opened by automation test software notice"
options.add_experimental_option("excludeSwitches", ["enable-automation"])

# chrome should successfully be initiated by this line, 
driver = webdriver.Chrome(service=chromeservice(driver_path),options=options)

# login on naukri
naukri_standard_url = 'https://www.naukri.com'
naukri_login_url = 'https://www.naukri.com/mnjuser/homepage'
driver.get(naukri_login_url)

# the below function shortens the syntax for driver.find_element() and for driver.find_elements() for ease ahead
def find(method='c',selector=None ):
    if method.lower() == "c":
        return driver.find_element('css selector',selector)
    elif method.lower() == "cm":
        return driver.find_elements('css selector',selector)
    elif method.lower() == "x":
        return driver.find_element('xpath',selector)
    elif method.lower() == "xm":
        return driver.find_elements('xpath',selector)
    elif method.lower() == "n":
        return driver.find_element('name',selector)
# function for logging out
def log_out():
    driver.delete_all_cookies()
    driver.get(driver.current_url)



# if naukri_login_url not in driver.current_url:
#     Login_but_selector = "#login_Layer"
#     email_field_selector = "#root > div > div > div > div > div > div > form > div:nth-child(2) > input"
#     pass_field_selector = "#root > div > div > div > div > div > div > form > div:nth-child(3) > input"
#     login_but = "#root > div > div > div > div > div > div > form > div:nth-child(6) > button"
#     find('c',Login_but_selector).click()
#     WebDriverWait(driver,3).until(EC.visibility_of_element_located((By.CSS_SELECTOR,email_field_selector))).send_keys('rishabsonak@gmail.com')
#     find('c',pass_field_selector).send_keys('Naukri@12345')
#     find('c',login_but).click()
#     WebDriverWait(driver,3).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"body > main > div > div > div.user-details.br-10.border.left-section > div > div.other-info-wrapper > div.view-profile-wrapper > a")))
# else:
#     email_field_selector = "#usernameField"
#     pass_field_selector = "#passwordField"
#     login_but = "#loginForm > div:nth-child(2) > div > div > button.waves-effect.waves-light.btn-large.btn-block.btn-bold.blue-btn.textTransform"
#     WebDriverWait(driver,3).until(EC.visibility_of_element_located((By.CSS_SELECTOR,email_field_selector))).send_keys('rishabsonak@gmail.com')
#     find('c',pass_field_selector).send_keys('Naukri@12345')
#     find('c',login_but).click()
#     WebDriverWait(driver,3).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"body > main > div > div > div.user-details.br-10.border.left-section > div > div.other-info-wrapper > div.view-profile-wrapper > a")))
#search_url_formation

# search URl for MIS
import re


def jobsearch(role_=None,expinyears=None,location_=None):
    base_url = 'https://www.naukri.com/'
    role = [re.sub(r'\s+', ' ', r.lower()).strip().replace(' ','-') for r in role_]
    role_string = '-'.join(role) + "-jobs"

    location = re.sub(r'\s+', ' ', location_[0].lower()).strip().replace(' ','-')
    location_string = '-in-' + location
    randldash = role_string + location_string + "?k="

    role = [re.sub(r'\s+', ' ', r.lower()).strip().replace(' ','%20') for r in role_]
    role_string = '%2C%20'.join(role)

    location = [re.sub(r'\s+', ' ', r.lower()).strip().replace(' ','%20') for r in location_]
    location_string = "&l=" + '%2C%20'.join(location)
    expinyears = 1
    poststring = role_string + location_string + f"&experience={expinyears}&nignbevent_src=jobsearchDeskGNB"

    jobsearchurl = f"{base_url}{randldash}{poststring}"
    # driver.get(jobsearchurl)
    return jobsearchurl

url = jobsearch(['Data Analyst','mis'],1,['noida'])
print(url)
import requests
from bs4 import BeautifulSoup

source_html = driver.page_source
# outermost_cards[i] - gets all the rows
def extract_job_data(cards):
    all_data = []
    for card in cards:
        
        data = {}
        a_tag = card.select_one('div.row1 > h2 > a')
        data['title'] = a_tag.text.strip()
        data['jobposting_url'] = a_tag['href']

        try:
            company_tag = card.select_one('div.row2 > span > a')
            data['company_page'] = company_tag['href']
            data['Posted by'] = company_tag.text.strip()
            reviews_available = True
        except:
            fallback_tag = card.select_one('div.row2 > div > a')
            data['company_page'] = fallback_tag['href']
            data['Posted by'] = fallback_tag.text.strip()
            reviews_available = False

        if reviews_available:
            rating_tag = card.select_one('div.row2 > span > a:nth-child(2) > span:nth-child(2)')
            reviews_tag = card.select_one('div.row2 > span > a:nth-child(3)')
            if rating_tag and reviews_tag:
                data['rating'] = rating_tag.text
                data['no_of_reviews'] = reviews_tag.text.replace('  Reviews', '')
                data['reviews_page_url'] = reviews_tag['href']
            else:
                data['rating'] = data['no_of_reviews'] = data['reviews_page_url'] = None
        else:
            data['rating'] = data['no_of_reviews'] = data['reviews_page_url'] = None

        exp = card.select_one('div.row3 > div.job-details > span.exp-wrap')
        data['experience'] = exp.text.replace(' Yrs', '') if exp else None

        salary = card.select_one('div.row3 > div.job-details > span.sal-wrap.ver-line > span > span')
        data['salary_offered'] = salary['title'].replace(' Lacs PA', '') if salary else None

        loc = card.select_one('div.row3 > div.job-details > span.loc-wrap.ver-line > span > span')
        data['location(s)'] = loc['title'] if loc else None

        overview = card.select_one('div.row4 > span')
        data['overview_text'] = overview.text.strip() if overview else None

        keywords = [li.text.strip() for li in card.select('div.row5 > ul > li')]
        data['key_words'] = ', '.join(keywords)

        post_day = card.select_one('div.row6 > span.job-post-day')
        data['days ago'] = post_day.text.strip() if post_day else None
        all_data.append(data)
        df = pd.DataFrame(all_data)
    return df





