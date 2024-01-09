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


# Define the header values

last_csv='./config/last_edisonba.csv'
last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)
    last = []

    for row in reader:
        last.append(row[0])
# Define the URL
main_file='output.csv'
base_url = "https://www.edisonba.com/pages/active-listings?page=1"


def fetch_data(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    try:
         # Get the page
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        title = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@style="font-size: 24pt;"]')))
        try:
            title = driver.find_element(By.XPATH, '//span[@style="font-size: 24pt;"]').text.strip()
        except:
            title = 'N/A'
        

        # Find the <div> element with the class "top-text"
        div_element = driver.find_element(By.CLASS_NAME,"top-text")

        # Extract the individual values by getting the inner text and splitting it by line breaks
        data_text = div_element.text.split('\n')

        city = 'N/A'
        state = 'N/A'
        country = 'N/A'
        try:
            location =data_text[3]
            if ',' in location:
                city,state=location.split(',')
            else:   
                country=location
        except Exception as e:
            location = 'N/A'
            print(f"An error occurred: {e}")

        print(city)
        source='edisonba.com'
        try:
            revenue=data_text[1]
        except:
            revenue='N/A'
        try:
            cashflow= data_text[2]
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
            desc=driver.find_element(By.XPATH,'//div[@class="listing-description"]').text
            decription=''.join(desc).strip()
        except:
            decription='N/A'
        try:
            listedby=driver.find_element(By.XPATH,'//div[@class="agent-name"]').text
            listedby=''.join(listedby).strip()
        except:
            listedby='N/A'
        try:
            listedby_firm=driver.find_element(By.XPATH,'//h3[@classxccac="media-heading"]//a/text()')[0]
            listedby_firm=''.join(listedby_firm).strip()
        except:
            listedby_firm='N/A'
        try:
            num=driver.find_element(By.XPATH,'//div[@class="agent-phone"]').text
            phone=''.join(num).strip() 
        except:
            phone='N/A'
        try:
            mail=driver.find_element(By.XPATH,'//div[@class="agent-phone"]').text
        except :
            mail='N/A'
        try:
            industry=driver.find_element(By.XPATH,'//div//span[text()="Category:"]/../../following-sibling::div[1]').text
        except:
            industry='N/A'
        try:
            ask=data_text[0]
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

        # check for cash flow 
        if '$' in cashflow:
            value = re.sub(r"[^\d\-+\.]", "", cashflow)
            rev = int(value)
            if rev >= 2000000:
                data_tocsv=[title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
                save_to_csv(data_tocsv)
        else:
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
    select_element = wait.until(EC.presence_of_element_located((By.XPATH, '//ul[@class="listings"]/li')))
    # time.sleep(4)
    limit=0 # check how many time we got revenue less than 4 million
    data=[]
    while True:
        results = driver.find_elements(By.XPATH, '//ul[@class="listings"]/li')


        try:
            for result in results:
                revenue_element = result.find_element(By.XPATH, './/h4[contains(text(),"REVENUE")]/following-sibling::p')
                revenue = revenue_element.text
                if '$' in revenue:
                    value = re.sub(r"[^\d\-+\.]", "", revenue)
                    rev = int(value)
                    if rev > 4000000:

                        atag_element = result.find_element(By.XPATH, './/span[@class="moreinfo legacyorange"]//a')
                        atag =  atag_element.get_attribute('href')
                        data.append(atag)
                    else:
                        limit+=1
                        if limit==150:
                            raise
                else:
                    
                    print("<---------------------->")

            # Handle next page logic
            try:
                driver.find_element(By.XPATH, '//a[@class="next_page"] disabled')
                break
            except:
                driver.find_element(By.XPATH, '//a[@class="next_page"]').click()

        except Exception as e:
            import traceback
            # traceback.format_exception
            print(str(traceback.format_exc()))
            break
            # next_page_url = None
            # return [], None
    return data

if __name__ == "__main__":
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    data = main_page(base_url,driver)
    unique=set(data)-set(last)
    if len(unique)>0:
        inside_page(list(unique))
        update_first(list(unique))
    driver.quit()
    print("Scraping completed.")

