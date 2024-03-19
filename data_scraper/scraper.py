from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd
import numpy as np


url = 'https://www.chrono24.ca/rolex/index-1.htm?pageSize=120&showpage=1'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

# IP check
url_check_ip = 'https://api.ipify.org/?format=json'
driver.get(url_check_ip)
page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")
ip_address = soup.find('body').text
print(ip_address)

# Try first page
driver.get(url)
html = driver.page_source
driver.quit()

complete_df = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/chrono/data/complete_url_df.csv')

options = webdriver.ChromeOptions()
# Config to work on Google Colab
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Pretend to be a non-headless browser
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
options.add_argument("--lang=en-US")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1280,720")

driver = webdriver.Chrome(options=options)

# check if the html is returned properly
driver.get('https://www.chrono24.ca/rolex/rolex-factory-diamond-dial--id33076260.htm')
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
len(str(soup)) 

start_num = 0
result = {}
# for i in range(complete_df.shape[0]):
for i in range(start_num, 10000):
    data_url = complete_df.iloc[i, 0]
    driver.get(data_url)
    # time.sleep(np.random.randint(1,10))
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    try:
        title = soup.find('h1', class_="h3 m-y-0").contents[0].strip()
    except:
        title = ''
    try:
        subtitle = soup.find('p', class_="text-md text-sm-lg").contents[0].strip()
    except:
        subtitle = ''
    try:
        rating = soup.find('span', class_='rating').contents[2].strip()
    except:
        rating = 0
    try:
        reviews = soup.find('button', class_="js-link-merchant-reviews link").contents[0].strip()
    except:
        reviews = 0
    try:
        description = soup.find('span', id='watchNotes').get_text(strip=True)
    except:
        description = ''

    content_table = soup.find('table')

    extracted_info = []
    # Loop through each tbody element to handle sections separately
    for tbody in content_table.find_all('tbody'):
        # Check if the section is 'Functions' by looking for a h3 tag
        section_header = tbody.find('h3')
        if section_header and 'Functions' in section_header.text:
            # Directly add the 'Functions' value
            functions = tbody.find('tr').find_next_sibling('tr').text.strip()
            extracted_info.append(('Functions', functions))
        else:
            # Extract other table data
            for tr in tbody.find_all('tr'):
                th = tr.find('strong')
                if th:
                    key = th.text.strip()
                    # Some values might be in 'a' tags or directly in 'td'
                    value = tr.find('td').find_next_sibling('td').text.strip()
                    extracted_info.append((key, value))
    if i % 100 == 0:
        flattened_data = {key: dict(value) for key, value in result.items()}
        result_df = pd.DataFrame.from_dict(flattened_data, orient='index')
        result_df.to_csv(f'/content/drive/MyDrive/Colab Notebooks/chrono/data/result_df_until_{i}.csv')

    # add more info outside the table
    extracted_info.append(('title', title))
    extracted_info.append(('subtitle', subtitle))
    extracted_info.append(('rating', rating))
    extracted_info.append(('reviews', reviews))
    extracted_info.append(('description', description))

    result[i+1] = extracted_info
    print(f'URL {i+1} completed')

    # save once every 100 urls
    if i % 100 == 0:
        flattened_data = {key: dict(value) for key, value in result.items()}
        result_df = pd.DataFrame.from_dict(flattened_data, orient='index')
        result_df.to_csv(f'/content/drive/MyDrive/Colab Notebooks/chrono/data/result_df_until_{i}.csv')


    flattened_data = {key: dict(value) for key, value in result.items()}
    result_df = pd.DataFrame.from_dict(flattened_data, orient='index')
    result_df.to_csv('/content/drive/MyDrive/Colab Notebooks/chrono/data/result_df_completed.csv')

# except:
#   flattened_data = {key: dict(value) for key, value in result.items()}
#   result_df = pd.DataFrame.from_dict(flattened_data, orient='index')
#   result_df.to_csv(f'/content/drive/MyDrive/Colab Notebooks/chrono/data/result_df_until_{result_df.shape[0] + start_num}.csv')