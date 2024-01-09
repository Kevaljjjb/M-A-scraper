import  csv
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pytz

mainfile="output.csv"
last_csv='./config/last_transworld.csv'
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
                location = driver.find_element(By.XPATH, '//span[text()="Location:"]/following-sibling::span').text.strip()
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    city=location
            except Exception as e:
                location = 'N/A'
                print(f"An error occurred: {e}")

            # print(city)
            source='transworld.com'
            try:
                revenue=driver.find_element(By.XPATH, '//span[text()="Total Sales:"]/following-sibling::span').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//span[text()="Sellers Discretionary Earnings:"]/following-sibling::span').text
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//span[text()="Inventory:"]/following-sibling::span').text
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,"//b[text()='EBITDA:']/following-sibling::b[1]").text
            except:
                ebitda='N/A'
            try:
                description=driver.find_element(By.XPATH,'//strong[text()="Description"]/../following-sibling::p[1]').text
            except:
                description = 'N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//span[text()="Phone:"]/../preceding-sibling::li').text
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'../following-sibling::p[1]').text
            except:
                listedby_firm='N/A'
            try:
                phone=driver.find_element(By.XPATH,'//span[text()="Phone:"]/following-sibling::span').text
            except:
                phone='N/A'
            try:
                mail=driver.find_element(By.XPATH,'//span[text()="Email:"]/following-sibling::span').text
            except:
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//span[text()="Category:"]/following-sibling::span').text.replace(" Businesses for Sale",'')
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[text()="Price:"]/following-sibling::span').text
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

def cashflow_revenue_checker(cash,rev):
    if '$' in cash:
        # print(cash)
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        try:
            value = float(value)
        except:
            return False
        if value >= 2000000:
            return True
        else:
            return False  # You were missing the return statement here
    elif '$'in rev:
        # print(cash)
        value = re.sub(r"[^\d\-+\.]", "", rev)
        # Convert the value to a float.
        try:
            value = float(value)
        except:
            return False
        if value >= 4000000:
            return True
        else:
            return False
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
    driver.get("https://www.tworld.com/buy-a-business/business-listing-search.php?country=United+States&state=&county=&category=&subcategory=&listing_price_min=&listing_price_max=&down_payment_price_min=&down_payment_price_max=&seller_price_min=2000000&seller_price_max=&formsubmit=1&s=Search&sort=-c_listing_price__c&items_per_page=50")
    # Find and store href and title data
    listings = driver.find_elements(By.XPATH, '//li[@class="result-item-wrapper paginate"]//a')
    for listing in listings:
        href = listing.get_attribute('href')
        urls.append(href)
    return urls

if __name__ == "__main__":
    allhref=main()
    unique_urls = set(allhref)-set(last) 
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    fetch_data(driver,unique_urls)
    update_first(unique_urls)