from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys 
import pytz
import time
import csv        
import re

last_csv='./config/last_axial.csv'

last=[]
last_count=0
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    for i in reader :
        last.append(i[0])

main_file="output.csv"
def cashflow_revenue_checker(cash):
    if '$' in cash:
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        value = float(value)
        # print("cash Flow is :", cash)
        if value >= 2.0 :            
            return True
        else :
            False
    else:
        return False  


def fetch_data(driver,url,desc):
        try:
            # driver.click()
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//table[@role="table"]/tbody/tr')))
            try:
                title = driver.find_element(By.XPATH, './td[4]').text.strip()
            except:
                title = 'N/A'

            city = 'N/A'
            state = 'N/A'
            country = 'USA'
            

            print(city)
            source='axial.com'
            try:
                revenue=driver.find_element(By.XPATH, './td[8]').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, "//div[text()='Cash Flow']/following-sibling::div").text.strip()
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//div[contains(text(),"Inventory")]/following-sibling::div/text()')[0]
                inventory=''.join(inventory).strip()
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'./td[9]').text
            except:
                ebitda='N/A'
            try:
                decription=desc
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
                industry=driver.find_element(By.XPATH,'//div//span[text()="Category:"]/../../following-sibling::div[1]').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[text()="Asking price"]/../following-sibling::div').text
            except:
                ask='N/A'
            current_datetime = datetime.now(pytz.utc)

            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)

            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%y")
            
            if cashflow_revenue_checker(ebitda):
                if url not in last:
                    data_tocsv=[title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
                    save_to_csv(data_tocsv)
                    update_first(url)

        except Exception as e:
            import traceback
            print(f"An error occurred while fetching data from {i}: {str(e)} \n")
            traceback_message = traceback.format_exc()
            print(traceback_message)
    
new_count=0
def save_to_csv(data):
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            writer=csv.writer(f)
            writer.writerow(data)

def  update_first(data):
     with open(last_csv,'a',newline='',encoding='utf-8')as f:
          w=csv.writer(f)
        #   w.writerow(headers)
          w.writerow([data])  
def login(driver):
    driver.get("https://network.axial.net/sign-in") 
    time.sleep(2.5)
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="email"]')))
    mail=driver.find_element(By.XPATH,'//input[@type="email"]')
    mail.send_keys("shawn@teddyholdings.com")
    time.sleep(2.5)
    pwd=driver.find_element(By.XPATH,'//input[@type="password"]')
    pwd.send_keys('Teddy123!')
    pwd.send_keys(Keys.ENTER)
    time.sleep(4)

def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    login(driver)
    time.sleep(3.5)
    driver.get("https://network.axial.net/received-deals/new")
    time.sleep(4)
    wait = WebDriverWait(driver, 20)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//table[@role="table"]/tbody/tr')))

    while True:
        trs = driver.find_elements(By.XPATH, '//table[@role="table"]/tbody/tr')
        for index in range(0,len(trs)):
            # Re-fetch the element by index every time to avoid stale reference
            wait.until(EC.element_to_be_clickable((By.XPATH, '//table[@role="table"]/tbody/tr')))
            trs = driver.find_elements(By.XPATH, '//table[@role="table"]/tbody/tr')
            tr = trs[index]
            tr.click()
            time.sleep(1.5)
            btn=wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@class="p--expand-label u-text-help"]')))
            btn.click()
            time.sleep(0.5)
            description = driver.find_element(By.XPATH, '//*[@class="ng-star-inserted"]/axl-teaser-description').text
            # print("description :", description)
            fetch_data(tr, driver.current_url, description)
            time.sleep(2)
            driver.find_element(By.XPATH,'//span[contains(@class,"ui-dialog-titlebar-close")]').click()
            driver.refresh()
            time.sleep(4)
        break

if __name__ == "__main__":
    main()