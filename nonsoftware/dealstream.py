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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

# Define the header values
headers = ['Title', 'City', 'State', 'Country', 'URL', 'Industry', 'Source', 'Description',
           'Listed By (Firm)', 'Listed By (Name)', 'Phone', 'Email', 'Price', 'Gross Revenue',
           'Cash Flow', 'Inventory', 'EBITDA','scraped Date']
last_csv='./config/last_dealstream.csv'
last=[]
last_count=0
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    header_skipped = False
    last = []

    for row in reader:
        if not header_skipped:
            header_skipped = True
            continue  # Skip the header line

        if any(row):  # Check if any element in the row is not empty
            if last_count ==0 :
                last.extend(row)



# Define the URL
main_file='output.csv'
base_url = "https://dealstream.com/search/businessforsale?page=1&updatecriteria=true&q=&profit.min=2000000&profit.max="


def fetch_data(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument(f'--headless')
    driver=webdriver.Chrome(options=options)
    try:
         # Get the page
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        title = wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
        try:
            title = driver.find_element(By.XPATH, '//h1').text.strip()
        except:
            title = 'N/A'

        city = 'N/A'
        state = 'N/A'
        country = 'N/A'
        try:
            location = driver.find_element(By.XPATH, '(//span[@data-original-title="Location"])[1]').text.strip()
            if ',' in location:
                city,state=location.split(',')
            else:   
                city=location
        except Exception as e:
            location = 'N/A'
            print(f"An error occurred: {e}")

        print(location)
        source='Dealstream.com'
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
            desc=driver.find_element(By.XPATH,'//span[@data-translatable="body"]').text
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
            # print(phone , url)
                    
        except:
            phone='N/A'
        mail='N/A'
        try:
            industry=driver.find_element(By.XPATH,'(//span[@data-original-title="Industry"])[1]').text
        except:
            industry='N/A'
        try:
            ask=driver.find_element(By.XPATH,'(//span[@data-original-title="Price"])[1]').text
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
                
def save_to_csv(data):
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            global new_count
            global  first
            writer=csv.writer(f)
            writer.writerow(data)
            print(new_count)
            new_count+=1
            if new_count==1:
                update_first(data)

def  update_first(data):
    with open(last_csv,'w',newline='',encoding='utf-8')as f:
          global  first
          w=csv.writer(f)
          w.writerow(headers)
          w.writerow(data)  
    
def inside_page(urls):

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks for each URL and collect the results
            executor.map(fetch_data, urls)

def login(driver):
    driver.get("https://dealstream.com/login")
    mail=driver.find_element(By.XPATH,'//input[@name="email"]')
    mail.send_keys("laherikeval273@gmail.com")
    pas=driver.find_element(By.XPATH,'//input[@name="pw"]')
    pas.send_keys("Keval@11")

    
    
def main_page(url,driver):
    # Navigate to the URL
    login(driver)
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    time.sleep(4)
    limit=0 # check how many time we got revenue less than 4 million
    data=[]
    while True:
        results = driver.find_elements(By.XPATH, '//div[@class="list-group-item post"]//a')


        try:
            for result in results:
                if len(last) >0 :
                    if last[4]== result.get_attribute("href") :
                        break
                data.append(result.get_attribute("href"))

            # Handle next page logic
            try:
                driver.find_element(By.XPATH, '//a[contains(text(),"Next") and not(contains(@class,"disabled"))]').click()
            except:
                try:
                    time.sleep(3)
                    driver.find_element(By.XPATH, '//a[contains(text(),"Next") and not(contains(@class,"disabled"))]').click()
                except:
                    print("Next button not found")
                    break
        except Exception as e:
            print(e)
            break
            # next_page_url = None
            # return [], None
    return data

if __name__ == "__main__":
    current_url = base_url
    first=[]    
    global new_count
    new_count=0  
    # Set the path to your Chrome WebDriver executable
    driver_path = "./config/chromedriver.exe"
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    options = uc.ChromeOptions()
    # options.add_argument(f"user-agent={user_agent}")
    options.headless = False
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    data = main_page(current_url,driver)
    # for i in data:
    #     fetch_data(i)

        # Fetch data from the current page
    inside_page(data)



    driver.quit()
    print("Scraping completed.")

# class="btn btn-default btn-sm disabled"
