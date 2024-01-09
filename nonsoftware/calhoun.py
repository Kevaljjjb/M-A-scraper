from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys 
import pytz
import time 
import re
import csv        


last_csv='./config/last_calhoun.csv'

last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader, None)
    for i in reader :
        last.append(i[0])

main_file="output.csv"

def fetch_data(urls):
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=Service(driver_path),options=options)
    driver.maximize_window()
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

            city = 'N/A'
            try:
                state=driver.find_element(By.XPATH,'//div[contains(text(),"Location")]/following-sibling::div').text
            except:
                state = 'N/A'
            country = 'N/A'
            

            source='calhoun.com'
            try:
                revenue=driver.find_element(By.XPATH, '//div[contains(text(),"Gross Sales")]/following-sibling::div').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//div[contains(text(),"Cash Flow")]/following-sibling::div').text
            except:
                cashflow='N/A'
            try:
                inventory=driver.find_element(By.XPATH,'//div[contains(text(),"Inventory")]/following-sibling::div/text()')[0]
                inventory=''.join(inventory).strip()
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//div[text()="Gross Income"]/following-sibling::div').text
            except:
                ebitda='N/A'
            try:
                decription=driver.find_element(By.XPATH,'//div[contains(text(),"Description")]/following-sibling::div/p').text
            except:
                decription='N/A'
            try:
                listedby=''
                listings=driver.find_elements(By.XPATH,'//div[@class="info"]/h4')
                for i in listings:
                    listedby += i.text  +" || "
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//div[@class="ct-personContent"]//h5')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                phone=''
                for i in driver.find_elements(By.XPATH,'//div[@class="info"]/a'):
                    phone +=  i.text +" || "
            except:
                phone='N/A'
            try:
                mail=driver.find_element(By.XPATH,'//i[@class="fa fa-envelope-o"]/following-sibling::a').text
            except:
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//div[contains(text(),"Industry")]/following-sibling::div').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//div[contains(text(),"Price")]/following-sibling::div').text
            except:
                ask='N/A'
            current_datetime = datetime.now(pytz.utc)

            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)

            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

            data_tocsv=[title,city,state,country,driver.current_url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
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

def cashflow_revenue_checker(cash):
    if '$' in cash:
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        value = int(value)
        # print("cash Flow is :", cash)
        if value > 1000000:            
            return True
        else :
            False
    else:
        return False  

def main():
    urls=[]
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=Service(driver_path),options=options)
    driver.get("https://www.calhouncompanies.com/find-a-business?ux_filter__node__field_industry=All&ux_filter__node__field_location=All&field_price_value=All&field_cash_flow_value=3")
    while True:
        hrefs=driver.find_elements(By.XPATH,'//a[@role="article"]')
        for href in hrefs:
            urls.append(href.get_attribute('href'))
        try:
            driver.find_element(By.XPATH,'//span[text()="››"]/..').click()
            time.sleep(3)
        except:
            break
    return urls


if __name__ == "__main__":
    urls=main()
    unique=set(urls)-set(last)
    if len(unique) >0:
        fetch_data(unique)  
        update_first(unique)