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
from lxml import html

# Define the header values
last_csv='./config/last_sybb.csv'
last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)

    for row in reader:
        last.append(row[0])

# Define the URL
main_file='output.csv'
base_url = "https://synergybb.com/search-results/?_sfm_price=0+80000000&_sfm_total_sales=0+90000000&_sfm_cash_flow=2000000+14000000"

def fetch_data(driver,urls):
    time.sleep(2)
    for i in urls:
        try:
            # Get the page
            driver.get(i)
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//h1[@itemprop="headline"]')))
            try:
                title = driver.find_element(By.XPATH, '//h1[@itemprop="headline"]').text.strip()
            except:
                title = 'N/A'

            city = 'N/A'
            state = 'N/A'
            country = 'N/A'
            try:
                location = driver.find_element(By.XPATH, '//strong[text()="Location:"]/..').text.strip().replace("LOCATION:","")
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    city=location
            except Exception as e:
                location = 'N/A'
                # print(f"An error occurred: {e}")

            # print(city)
            source='synergybb.com'
            try:
                revenue=driver.find_element(By.XPATH, '//strong[text()="Annual Revenue:"]/..').text.strip().replace("ANNUAL REVENUE:","")
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//strong[text()="Net Cash Flow:"]/..').text.strip().replace("NET CASH FLOW:","")
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//strong[text()="Inventory:"]/..').text.replace("Inventory:","")
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//div[text()="Gross Income"]/following-sibling::div').text
            except:
                ebitda='N/A'
            try:
                desc = driver.find_elements(By.XPATH, '//div[@itemprop="text"]//p[not(.//strong)]')

                # Extract text from each element
                description_texts = [element.text for element in desc]

                # Concatenate the text content
                description = ''.join(description_texts).strip()
            except:
                description='N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//h3[@class="text-center broker-name"]/strong').text
                listedby=''.join(listedby).strip()
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                element = driver.find_element(By.XPATH, '//p[@class="text-center"]')
                text_content = element.text
                lines = text_content.split('Email:')
                phone = None
                mail = None

                # Iterating through the lines to find the phone number and email
                for line in lines:
                    if 'Cell:' in line:
                        phone = line.split('Cell:')[1].strip()
                    elif '\n' in line:
                        mail = line.strip().replace("\n","")
            except:
                phone='N/A'
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//div//span[text()="Category:"]/../../following-sibling::div[1]').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//strong[text()="Price:"]/..').text.replace("PRICE:","")
            except:
                ask='N/A'
            
            # code to get the date from the edt time
            # Get the current date and time in UTC
            current_datetime = datetime.now(pytz.utc)

            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)

            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

            data_tocsv=[title,city,state,country,i,industry,source,description,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
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
    driver.get(base_url)
    urls=[]
    for i in driver.find_elements(By.XPATH,'//a[text()="Learn More"]'):
        urls.append(i.get_attribute("href"))
    return urls

if __name__ =="__main__":
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    links=main(driver)
    unique=set(links)-set(last)
    fetch_data(driver,unique)
    update_first(unique)
    driver.close()