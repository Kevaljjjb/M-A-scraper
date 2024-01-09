import requests
from lxml import html
import  csv
import time
import concurrent.futures
import re
import pytz
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

last_csv='./config/last_globalx.csv'
last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)

    for row in reader:
        last.append(row[0])

# Define the URL
main_file='output.csv'
base_url = "http://www.globalbx.com/results.asp?q=YzE9MjAwMDAwMCZibG9jPTAmdD0w"

def fetch_data(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        title = wait.until(EC.presence_of_element_located((By.XPATH, '//font[@size="4"]')))
        try:
            title = driver.find_element(By.XPATH, '//font[@size="4"]').text.strip()
        except:
            title = 'N/A'

        city = 'N/A'
        state = 'N/A'
        country = 'N/A'
        try:
            element = driver.find_element(By.XPATH, '//b[contains(text(),"Location")]').text
            location = element.split("Location:")[1].split("Industry:")[0].strip()
            industry = element.split("Industry:")[1].strip()
 
            country=location
        except Exception as e:
            location = 'N/A'
            print(f"An error occurred: {e}")

        print(location)
        source='Globalx.com'
        try:
            revenue=driver.find_element(By.XPATH, '(//font[@size="2"]/b[ contains(text(),"Gross Revenues")]/../following-sibling::font)[1]').text.strip()
        except:
            revenue='N/A'
        try:
            cashflow=driver.find_element(By.XPATH,'(//font[@size="2"]/b[ contains(text(),"Cash Flow:")]/../following-sibling::font)[1]').text.strip()
        except:
            cashflow='N/A'

        try:
            inventory=driver.find_element(By.XPATH,'//div[contains(text(),"Inventory")]/following-sibling::div/text()')[0]
            inventory=''.join(inventory).strip()
        except:
            inventory='N/A'
        try:
            ebitda=driver.find_element(By.XPATH,"//b[contains(text(),'EBITDA:')]/following-sibling::b[1]/text()")[0]
        except:
            ebitda='N/A'
        try:
            desc=driver.find_element(By.XPATH,'//div[@class="KonaBody"]').text
            decription=''.join(desc).strip()
        except:
            decription='N/A'
        try:
            listedby=driver.find_element(By.XPATH,'//div[@class="brokerName"]').text
            listedby=''.join(listedby).strip()
        except:
            listedby='N/A'
        try:
            listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
            listedby_firm=''.join(listedby_firm).strip()
        except:
            listedby_firm='N/A'
        try:
            num=driver.find_element(By.XPATH,'//a[@class="officeNum"]').text
            phone=''.join(num).strip()
            if phone =='':
                num=driver.find_element(By.XPATH,'//a[@class="cellNum"]').text
                phone=''.join(num).strip()
        except:
            phone='N/A'
        mail='N/A'
        try:
            industry=driver.find_element(By.XPATH,'//div//span[text()="Category:"]/../../following-sibling::div[1]').text
        except:
            industry='N/A'
        try:
            ask=driver.find_element(By.XPATH,'(//font[@size="2"]/b[ contains(text(),"Asking Price Range")]/../following-sibling::font)[1]').text
        except:
            ask='N/A'
        driver.quit()
        # code to get the date from the edt time
        # Get the current date and time in UTC
        current_datetime = datetime.now(pytz.utc)

        # Convert to Eastern Daylight Time (EDT)
        eastern = pytz.timezone("US/Eastern")
        current_datetime_edt = current_datetime.astimezone(eastern)

        # Format the date as mm/dd/yy
        formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

        data_tocsv=[title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
        save_to_csv(data_tocsv)

    except Exception as e:
        import traceback
        print(f"An error occurred while fetching data from {url}: {str(e)} \n")
        traceback_message = traceback.format_exc()
        print(traceback_message)
        driver.quit()

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
    
def inside_page(urls):

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks for each URL and collect the results
            executor.map(fetch_data, urls)

def main_page(url,driver):
    # Navigate to the URL
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.XPATH, '//table[@id="lt"]//tr//td[2]/a[not(contains(., "Read More"))]')))
    # time.sleep(4)
    js="window.scrollBy(0,550);"
    driver.execute_script(js)
    time.sleep(4)
    limit=0 # check how many time we got revenue less than 4 million
    data=[]
    while True:
        results = driver.find_elements(By.XPATH, '//table[@id="lt"]//tr//td[2]/a[not(contains(., "Read More"))]')
        try:
            for result in results:
                data.append(result.get_attribute("href"))

            # Handle next page logic
            try:
                driver.find_element(By.XPATH, '(//a[text()="Next"])[1]').click()
            except:
                try:
                    time.sleep(3)
                    driver.find_element(By.XPATH, '(//a[text()="Next"])[1]').click()
                except:
                    print("Next button not found")
                    break
        except Exception as e:
            print(e)
            break
    return data

if __name__ == "__main__":
    first=[]
    driver_path = "./config/chromedriver.exe"
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    data = main_page(base_url,driver)
    unique=set(data)-set(last)
    if len(unique)>0:
        inside_page(unique)
        update_first(unique)
    driver.quit()
    print("Scraping completed.")
