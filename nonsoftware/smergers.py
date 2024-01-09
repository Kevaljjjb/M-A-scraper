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
import re
import csv        


last_csv='./config/last_smergers.csv'
last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader, None)
    for i in reader :
        last.append(i[0])
main_file="output.csv"

def cashflow_revenue_checker(cash):
    if '$' in cash:
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        value = int(value)
        # print("cash Flow is :", cash)
        if value > 2000000:            
            return True
        else :
            False
    else:
        return False  

def extract_highest_value(data):
    if "-" in data:
        revenue=int(data.split("-")[1].replace(" million",''))
    else:
        revenue=int(data.replace("USD ",'').replace(" million",''))

    return revenue if revenue else None
    
def fetch_data(urls,driver):
    for i in urls:
        try:
            # Get the page
            driver.get(i)
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '(//span[@class="asking-price"])[1]')))
            try:
                title = driver.find_element(By.XPATH, '//h1').text
            except:
                title = 'N/A'

            state = 'N/A'
            country = 'N/A'
            try:
                city=driver.find_element(By.XPATH,'//td[text()="Locations"]/following-sibling::td/span').get_attribute('data-title')
            except:
                city="N/A"
            
            source='smergers.com'
            try:
                rev=driver.find_element(By.XPATH, '//td[contains(text(),"Reported Sales")]/following-sibling::td').text
                revenue_value= extract_highest_value(rev)
                revenue="$"+str(revenue_value)+" Mil"
            except:
                revenue='N/A'
                revenue_value=0
            try:
                cashflow=driver.find_element(By.XPATH, '//p[contains(text(),"Cashflow: ")]').text.replace("Cashflow: ","")
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//div[contains(text(),"Inventory")]/following-sibling::div/text()')[0]
                inventory=''.join(inventory).strip()
            except:
                inventory='N/A'
            try:
                if revenue_value is not None:
                    ebitda_percentage=int(driver.find_element(By.XPATH,'//td[contains(text(),"EBITDA Margin")]/following-sibling::td').text.replace("%",""))
                    ebitda_value=ebitda_percentage/100*revenue_value
                    ebitda="$"+str(ebitda_value)+" Mil"
                else:
                    ebitda="N/A"
            except:
                ebitda='N/A'
            try:
                decription=driver.find_element(By.XPATH,'(//div[@itemprop="description"])[1]').text
            except:
                decription='N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//div[@class="ct-personContent"]//h5').text
                listedby=''.join(listedby).strip()
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//div[@class="ct-personContent"]//h5')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                phone=driver.find_element(By.XPATH,'//div[@class="ct-personContent"]//i[@class="fa fa-phone"]/following-sibling::a[1]').text
            except:
                phone='N/A'
            try:
                mail=driver.find_element(By.XPATH,'//i[@class="fa fa-envelope-o"]/following-sibling::a').text
            except:
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//td[contains(text(),"Industries")]/following-sibling::td/span').get_attribute('data-title')
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'(//span[@class="asking-price"])[1]').text
            except:
                ask='N/A'
            try:
                sourcelink=driver.find_element(By.XPATH,'//a[text()="here"]').get_attribute('href')
            except:
                sourcelink=''
            current_datetime = datetime.now(pytz.utc)

            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)

            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")
            data_tocsv=[title,city,state,country,driver.current_url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date,'',sourcelink]
            save_to_csv(data_tocsv)

        except Exception as e:
            import traceback
            print(f"An error occurred while fetching data from {i}: {str(e)} \n")
            traceback_message = traceback.format_exc()
            print(traceback_message)
            continue

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
def login(driver):
    driver.get("https://www.smergers.com/login/")
    time.sleep(3)
    driver.find_element(By.XPATH,'(//li[@data-tab="login"])[1]').click()
    time.sleep(1.5)
    email=driver.find_element(By.XPATH,'(//input[@name="login-username"])[1]')
    email.send_keys("mary@teddyholdings.com")
    password=driver.find_element(By.XPATH,'(//input[@name="login-password"])[1]')
    password.send_keys("Teddy1539")
    password.send_keys(Keys.ENTER)

def main(driver):
    urls=[]
    login(driver)
    driver.get("https://www.smergers.com/businesses-for-sale-and-investment-opportunities-in-north-america/c65b/?ebitda_gte=2000000&ebitda_lte=100000000")
    while True:
        time.sleep(3)
        results=driver.find_elements(By.XPATH,'//span[contains(text(),"Contact Business")]')
        print("page URL :",driver.current_url)
        for result in results:
            urls.append("https://www.smergers.com"+result.get_attribute('href'))
        try:
            adder=driver.find_element(By.XPATH,'//li[not(contains(@class,"disabled"))]/a[contains(text(),"Next")]').get_attribute('href')
            driver.get(adder)
        except Exception as e:
            break
    return urls


if __name__ == "__main__":
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    urls=main(driver)
    unique=set(urls)-set(last)
    if len(unique) >0:
        fetch_data(unique,driver)
        update_first(unique)