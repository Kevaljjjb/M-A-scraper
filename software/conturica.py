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
import time

mainfile="soft_data.csv"
last_csv='./config/last_conturica.csv'
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
            title = wait.until(EC.presence_of_element_located((By.XPATH, '(//h2)[1]')))
            try:
                title = driver.find_element(By.XPATH, '(//h2)[1]').text
            except:
                title = 'N/A'

            city = 'N/A'
            state = 'N/A'
            country = 'N/A'
            try:
                location = driver.find_element(By.XPATH, '//th[text()="Location"]/following-sibling::td').text
                if ',' in location:
                    country,state=location.split(',')
                else:   
                    state=location
            except Exception as e:
                location = 'N/A'
                print(f"An error occurred: {e}")

            # print(city)
            source='centurica.com'
            try:
                revenue=driver.find_element(By.XPATH, '//strong[contains(text(),"Annual Gross Revenue ")]/..').text.replace("Annual Gross Revenue :\n",'')
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//th[text()="Cash Flow"]/following-sibling::td').text
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//strong[contains(text(),"Inventory Value")]/..').text.replace("Inventory Value:\n","")
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//strong[contains(text(),"Annual Net Profit ")]/..').text.replace("Annual Net Profit :\n","")
            except:
                ebitda='N/A'
            try:
                desc=driver.find_elements(By.XPATH,'//h5[text()="Description"]/following-sibling::p[position() <= 4]')
                description=''.join(desc)
            except:
                description = 'N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//a[@class="borkerLink"]').text
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                main_phone=driver.find_element(By.XPATH,'//label[contains(text(),"Phone:")]/..').text
                mobile=driver.find_element(By.XPATH,'//label[contains(text(),"Mobile:")]/..').text
                phone=main_phone+"\n"+mobile
                        
            except:
                phone='N/A'
            try:
                mail=driver.find_element(By.XPATH,'//label[contains(text(),"Email:")]/following-sibling::a').text
            except:
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//th[text()="Industry"]/following-sibling::td').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//strong[contains(text(),"Asking Price ")]/..').text.replace("Asking Price :\n","")
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

def cashflow_revenue_checker(cash):
    if '$' in cash:
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        value = int(value)
        # print("cash Flow is :", cash)
        if value > 500000:            
            return True
        else :
            False
    else:
        return False  

def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    wait = WebDriverWait(driver, 10)
    urls=[]
    driver.get('https://app.centurica.com/marketwatch')
    driver.maximize_window()
    time.sleep(4)
    try:
        driver.find_element(By.XPATH,'//*[@id="email_bounce_close"]').click()
    except:
        print('no Button')

    filter=driver.find_element(By.XPATH,'//input[@id="filter_revenue_min"]')
    filter.send_keys(1000000)
    while True:
        listings = driver.find_elements(By.XPATH, '//table[@id="table-listings"]/tbody/tr')
        for listing in listings:
            date=listing.find_element(By.XPATH,'./td[1]').text
            if "Sep" in date :
                break
            href = listing.find_element(By.XPATH,'./td[2]/a[1]').get_attribute('href')
            urls.append(href)
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
    fetch_data(driver,unique_urls)
    if len(unique_urls)>0:
        update_first(unique_urls)