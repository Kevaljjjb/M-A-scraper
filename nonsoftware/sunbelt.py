from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
import pytz
import time 
import re
import csv        


last_csv='./config/last_sunbelt.csv'

last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader, None)
    for i in reader :
        last.append(i[0])

main_file="output.csv"

def fetch_data(urls,driver):
    # driver_path = "./config/chromedriver.exe"
    # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    # options = webdriver.ChromeOptions()
    # options.add_argument(f'user-agent={user_agent}')
    # # options.add_argument(f'--headless')
    # driver=webdriver.Chrome(service=Service(driver_path),options=options)
    time.sleep(2)
    for i in urls:
        try:
            # Get the page
            driver.get(i)
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
            try:
                title = driver.find_element(By.XPATH, '//h1').text.strip()
            except:
                title = 'N/A'
            
            country = 'N/A'
            try:
                city=driver.find_element(By.XPATH,'//strong[text()="City:"]/following-sibling::span').text
            except:
                city="N/A"
            try:
                state=driver.find_element(By.XPATH,'//strong[text()="State:"]/following-sibling::span').text
            except:
                state="N/A"

            source='sunbeltnetwork.com'
            try:
                revenue=driver.find_element(By.XPATH, '//span[contains(text(),"Gross Revenue")]/preceding-sibling::strong[@class]').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//span[contains(text(),"Cash Flow")]/preceding-sibling::strong[@class]').text
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//strong[contains(text(),"Inventory Value:")]/following-sibling::span').text
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//strong[contains(text(),"Adjusted EBITDA:")]/following-sibling::span').text
            except:
                ebitda='N/A'
            try:
                decription=driver.find_element(By.XPATH,'//ul[@class="resultsBusiness__otherCategories"]/following-sibling::p').text
            except:
                decription='N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//figure/following-sibling::div/h5').text
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                phone=driver.find_element(By.XPATH,'//span[@id="numberPhone"]/following-sibling::a').get_attribute('href').replace('tel:','')
            except:
                phone='N/A'
            try:
                mail=driver.find_element(By.XPATH,'//a[contains(@href,"mailto:")]').get_attribute('href').replace('mailto:','')
            except:
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//div[@data-id="fb459aa"]').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[contains(text(),"Asking Price")]/preceding-sibling::strong[@class]').text
            except:
                ask='N/A'
            current_datetime = datetime.now(pytz.utc)

            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)

            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

            data_tocsv=[title,city,state,country,i,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
            save_to_csv(data_tocsv)

        except Exception as e:
            import traceback
            print(f"An error occurred while fetching data from {i}: {str(e)} \n")
            traceback_message = traceback.format_exc()
            print(traceback_message)
            continue

    return []
new_count=0
def save_to_csv(data):
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            writer=csv.writer(f)
            writer.writerow(data)

def  update_first(data):
     with open(last_csv,'a',newline='',encoding='utf-8')as f:
          w=csv.writer(f)
          for i in data:
            w.writerow([i])  

def main(driver):
    urls=[]
    driver.get("https://www.sunbeltnetwork.com/business-search/business-results/")
    driver.maximize_window()
    time.sleep(3)
    driver.find_element(By.XPATH,'//select[@id="countryHome"]/option[@value="United States"]').click()
    driver.find_element(By.XPATH,'//a[@id="buttonAdvancedSearch"]').click()
    time.sleep(1)
    driver.find_element(By.XPATH,'//select[@id="dateAdded"]/option[@value="This Year"]').click()
    time.sleep(1)
    filter_cf=driver.find_element(By.XPATH,'//input[@id="cf-min"]')
    filter_cf.send_keys(2000000)
    time.sleep(1)
    try:
        driver.find_element(By.XPATH,'//input[@value="Search"]').click()
    except:
        try:
            driver.find_element(By.XPATH,'//input[@value="Search"]').click()
        except:
            return []
            
    driver.find_element(By.XPATH,'//a[@id="buttonAdvancedSearch"]').click()
    time.sleep(2.5)
    while True:
        try:
            driver.find_element(By.XPATH,'//div[@class="responseLoader" and @style="display: none;"]')
            break
        except:
            time.sleep(5)
            continue

    hrefs=driver.find_elements(By.XPATH,'//a[contains(text(),"View Listing")]')
    for i in hrefs:
        urls.append(i.get_attribute('href'))

    return urls


if __name__ == "__main__":
    # options = uc.ChromeOptions()
    # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")
    # options.headless = False
    driver = uc.Chrome()
    # driver=webdriver.Chrome()
    urls=main(driver)
    unique=set(urls)-set(last)
    # print(len(set(urls)))
    if len(unique)>0:
        fetch_data(unique,driver)
        update_first(unique)
    driver.close()

# Keval@11_Teddy1539!