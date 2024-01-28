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
last_csv='./config/last_bizbuysell.csv'
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
            if "Business-Auction" in i: continue
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
                location = driver.find_element(By.XPATH, '//h2[@class="gray"]').text.strip()
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    city=location
            except Exception as e:
                location = 'N/A'
                print(f"An error occurred: {e}")

            # print(city)
            source='Bizbuysell.com'
            try:
                revenue=driver.find_element(By.XPATH, '//span[contains(text(), "Gross Revenue:")]/following-sibling::b').text
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
                ebitda=driver.find_element(By.XPATH,"//span[contains(text(), 'EBITDA:')]/following-sibling::b").text
            except:
                ebitda='N/A'
            try:
                description=driver.find_element(By.XPATH,'//div[@class="businessDescription"]').text
            except:
                description = 'N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//h3[contains(text()," Listed By:")]').text.replace("Listed By:",'').replace("Business",'').strip()
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                phone=driver.find_element(By.XPATH,'//a[contains(text(), "Phone Number")]/following-sibling::label/a').get_attribute("href").replace("tel:",'')
                # print(phone , url)
                        
            except:
                phone='N/A'
            mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//p[@class="industry"]').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[contains(text(), "Asking Price:")]/following-sibling::b').text
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
            if '$' not in cashflow and '$' not in revenue and '$' not in ebitda and asking_checker(ask):
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

def asking_checker(ask):
    if '$' in ask:
        # print(ask)
        value = re.sub(r"[^\d\-+\.]", "", ask)
        # Convert the value to a float.
        try:
            value = float(value)
        except:
            return False
        if value >= 6000000:
            return True
        else:
            return False  # You were missing the return statement here
    else:
        return False
    

def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    wait = WebDriverWait(driver, 10)
    urls=[]
    driver.get("https://www.bizbuysell.com/businesses-for-sale/?q=cGZyb209NjAwMDAwMA%3D%3D")
    while True:
        # Find and store href and title data
        listings = driver.find_elements(By.XPATH, '//div[@class="listing-container"]//a[@applistingclick]')
        for listing in listings:
            # title = listing.get_attribute('title')
            try:
                listing.find_element(By.XPATH,'.//p[contains(text(),"Cash Flow:")]')
                continue
            except:
                href = listing.get_attribute('href')
                # csv_writer.writerow([title, href])
                urls.append(href)
        
        # Find next page button and click it
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        try :
            try:
                driver.find_element(By.XPATH, '//a[@class="close-icon-modal"]').click()
            except:
                print("No ad")

            next_button = driver.find_element(By.XPATH, '//a[@class="bbsPager_next ng-star-inserted"]')
            next_button.click()
            print("Button clicked")
            
            time.sleep(5)
        except:
            break
    return urls

if __name__ == "__main__":
    allhref=main()
    unique_urls = set(allhref)-set(last) 
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    if len(unique_urls)>0:
        fetch_data(driver,unique_urls)
        update_first(unique_urls)