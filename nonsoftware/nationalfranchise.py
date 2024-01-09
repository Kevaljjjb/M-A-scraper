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


last_csv='./config/last_nationalfranchise.csv'

last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader, None)
    for i in reader :
        last.append(i[0])

main_file="output.csv"
def login(driver):
    driver.find_element(By.XPATH,'//b[text()="Login"]/..').click()
    time.sleep(3)
    username=driver.find_element(By.XPATH,'//input[@id="j_username"]')
    username.send_keys("mary@teddyholdings.com")
    time.sleep(3)
    password=driver.find_element(By.XPATH,'//input[@id="j_password"]')
    password.send_keys("Teddy1539")
    time.sleep(3)
    driver.find_element(By.XPATH,'//button[@id="login-button"]').click()


def fetch_data(urls,driver):
    for i in urls:
        try:
            driver.get(i)
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//img/following-sibling::h3')))
            try:
                title = driver.find_element(By.XPATH, '//img/following-sibling::h3').text.strip()
            except:
                title = 'N/A'

            city = 'N/A'
            try:
                state=driver.find_element(By.XPATH,'//div[contains(text(),"Location")]/following-sibling::div').text
            except:
                state = 'N/A'
            country = 'N/A'
            

            source='nationalfranchiseforsale.com'
            try:
                revenue=driver.find_element(By.XPATH, '//div[contains(text(),"Gross Sales")]/following-sibling::div').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//span[contains(text(),"Cash")]/following-sibling::span').text
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
                decription=driver.find_element(By.XPATH,'//h2[text()="Additional Information"]/../following-sibling::div').text
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
                ask=driver.find_element(By.XPATH,'//span[contains(text(),"Price")]/following-sibling::span').text
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

def main(driver):
    urls=[]
    driver.get("https://www.nationalfranchisesales.com/listings")
    driver.maximize_window()
    login(driver)

    time.sleep(2)
    driver.find_element(By.XPATH,'//a[contains(text(),"Additional Filters")]').click()
    time.sleep(4)
    driver.execute_script("window.scrollBy(0,400);")
    driver.execute_script('''btn=document.querySelector('input[name="$2M - $10M EBITDA"]'); btn.click();''')
    time.sleep(1)
    driver.execute_script('''btn=document.querySelector('input[name="$10M+ EBITDA'); btn.click();''')
    time.sleep(1)
    while True:
        hrefs=driver.find_elements(By.XPATH,'//tr/td[not(@style="display: none;") and not(@class="dataTables_empty")]/../td[1]')
        for href in hrefs:
            if href.get_attribute('data-href'):
                link= href.get_attribute('data-href')
            else:
                link=''
            urls.append("https://www.nationalfranchisesales.com"+link)
        try:
            driver.find_element(By.XPATH,'//i[@class="fa fa-angle-right"]/..').click()
            time.sleep(3)
        except:
            break
    return urls


if __name__ == "__main__":
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    urls=main(driver)
    unique=set(urls)-set(last)
    if len(unique) >0:
        fetch_data(unique,driver)  
        update_first(unique)
