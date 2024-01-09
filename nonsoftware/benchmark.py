import  csv
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import pytz
import time

mainfile="output.csv"
last_csv='./config/last_benchmark.csv'
last=[]
new_count=0 
last_count=0
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    last = []

    for row in reader:
        last.append(row[0])
        
def fetch_data(driver,urls):
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

            city = 'N/A'
            state = 'N/A'
            country = 'N/A'
            try:
                location = driver.find_element(By.XPATH, '//div[@class="job_listing-location job_listing-location-formatted"]').text.strip()
                if ',' in location:
                    state,country=location.split(',')
                else:   
                    country=location
            except Exception as e:
                location = 'N/A'
                print(f"An error occurred: {e}")
            source='Benchmark.com'
            try:
                revenue=driver.find_element(By.XPATH, '//b[text()="REVENUE/TURNOVER:"]/..').text.replace("REVENUE/TURNOVER:","")
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//span[contains(text(), "Cash Flow:")]/following-sibling::b').text
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//span[contains(text(), "Inventory:")]/following-sibling::b').text
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//b[text()="EBITDA:"]/..').text.replace("EBITDA:","")
            except:
                ebitda='N/A'
            try:
                description=driver.find_element(By.XPATH,'id="listify_widget_panel_listing_content-1"').text
            except:
                description = 'N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//div[@class="job_listing-author-info"]').text
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                phone=driver.find_element(By.XPATH,'//div[@class="job_listing-phone"]//a[contains(@href,"tel:")]').text
            except:
                phone='N/A'
            try:
                mail=driver.find_element(By.XPATH,'//div[@class="listing-email"]//a[contains(@href,"mailto:")]').text
            except:
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//p[@class="industry"]').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[contains(text(), "Asking Price:")]/following-sibling::b').text
            except:
                ask='N/A'
            current_datetime = datetime.now(pytz.utc)

            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)

            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

            data_tocsv=[title,city,state,country,driver.current_url,industry,source,description,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
            save_to_csv(data_tocsv)

        except Exception as e:
            import traceback
            print(f"An error occurred while fetching data from {i}: {str(e)} \n")
            traceback_message = traceback.format_exc()
            print(traceback_message)
            continue
    return []
def save_to_csv(data):
    with open(mainfile,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            global new_count
            writer=csv.writer(f)
            writer.writerow(data)

def  update_first(data):
     with open(last_csv,'a',newline='')as f:
          w=csv.writer(f)
          for i in data:
            w.writerow([i])     

def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    wait = WebDriverWait(driver, 10)
    urls=[]
    driver.get("https://embracebenchmark.com/opportunities/?fwp_region=us&fwp_ebitda=ebitda-2m-5m%2Cebitda-5m-10m%2Cebitda-10m-25m%2Cebitda-25m")
    while True:
        # Find and store href and title data
        listings = driver.find_elements(By.XPATH, '//a[@class="job_listing-clickbox"]')
        for listing in listings:
            # title = listing.get_attribute('title')
            href = listing.get_attribute('href')
            # csv_writer.writerow([title, href])
            urls.append(href)
        
        # Find next page button and click it
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        try :
            next_button = driver.find_element(By.XPATH, '//a[text()=">>"]')
            next_button.click()
            
            time.sleep(4)
        except Exception as e:
            print(str(e))
            break
    return urls

if __name__ == "__main__":
    allhref=main()
    # print(allhref)
    unique_urls = set(allhref)-set(last) 
    update_first(unique_urls)
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    fetch_data(driver,unique_urls)