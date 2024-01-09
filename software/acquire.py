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


last_csv='./config/acquire_urls.csv'

last=[]
last_count=0
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    # last=list(reader)
    for i in reader :
        last.append(i[0])

main_file="soft_data.csv"

def fetch_data(urls):
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    login(driver)
    time.sleep(2)
    for i in urls:
        try:
            # Get the page
            driver.get(i)
            wait = WebDriverWait(driver, 6)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="body-p1-medium c-smoke"]')))
            try:
                title = driver.find_element(By.XPATH, '//span[@class="body-p1-medium c-smoke"]').text.strip()
            except:
                title = 'N/A'

            city = 'N/A'
            state = 'N/A'
            country = 'N/A'
            

            print(city)
            source='acquire.com'
            try:
                revenue=driver.find_element(By.XPATH, '//span[text()="TTM revenue"]/following-sibling::div').text.strip()
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
                ebitda=driver.find_element(By.XPATH,'//div[text()="Gross Income"]/following-sibling::div').text
            except:
                ebitda='N/A'
            try:
                desc=driver.find_element(By.XPATH,'//meta[@name="description"]').get_attribute("content")
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
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

            data_tocsv=[title,city,state,country,i,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
            save_to_csv(data_tocsv)

        except Exception as e:
            import traceback
            print(f"An error occurred while fetching data from {i}: {str(e)} \n")
            traceback_message = traceback.format_exc()
            print(traceback_message)
            continue

    return []
def save_to_csv(data):
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            writer=csv.writer(f)
            writer.writerow(data)

def login(driver):
    driver.get("https://app.acquire.com/signin") 
    time.sleep(2.5)
    mail=driver.find_element(By.XPATH,'//*[@inputmode="email"]')
    mail.send_keys("laherikeval273@gmail.com")
    time.sleep(2.5)
    pwd=driver.find_element(By.XPATH,'//*[@inputmode="text"]')
    pwd.send_keys('Keval@11')
    pwd.send_keys(Keys.ENTER)
    time.sleep(4)

def main():
    urls=[]
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    login(driver)
    driver.get("https://app.acquire.com/all-listing")
    driver.maximize_window()
    time.sleep(5)
    method='''
    function scrollToPageBottom() {
        window.scrollTo(0, document.body.scrollHeight);
    }
    scrollToPageBottom();
    '''
    time.sleep(3)

    # //a[@class="marketplace-card marketplace-card--all-listing"]//span[text()="TTM REVENUE"]/following-sibling::span
    # if this become true then break the loop and get links 
    # //a[@class="marketplace-card marketplace-card--all-listing"]//span[text()="TTM REVENUE"]/following-sibling::span[contains(text(),'k')]
    while True:
        if driver.find_elements(By.XPATH,'//a[@class="marketplace-card marketplace-card--all-listing"]//span[text()="TTM REVENUE"]/following-sibling::span[contains(text(),"k")]'):
            break
        else:
            driver.execute_script(method)
            time.sleep(1.7)

    hrefs=driver.find_elements(By.XPATH,'//a[@class="marketplace-card marketplace-card--all-listing"]//span[text()="TTM REVENUE"]/following-sibling::span[contains(text(),"M")]/../../..')
    allhref=[i.get_attribute("href") for i in hrefs]

    driver.quit()
    return allhref

def add_all(data):
    with open(last_csv,"a",newline='')as f:
        writer=csv.writer(f)
        for i in data:
            writer.writerow([i])
if __name__ == "__main__":
    links=main()
    unique=set(links)-set(last)
    if len(unique)>0:
        fetch_data(unique)
        add_all(unique)
# //span[@class="cache-flow-value"]
# //a[text()="LEARN MORE »"]