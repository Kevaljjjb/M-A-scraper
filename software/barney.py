from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pytz
import  re
from datetime import datetime
import csv
import time

last_csv='./config/last_barney.csv'
last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)

    for row in reader:
        last.append(row[0])

# Define the URL
main_file='soft_data.csv'


    
def fetch_data(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    try:
         # Get the page
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        title = wait.until(EC.presence_of_element_located((By.XPATH, '(//h2[@class="h2"]/span)[1]')))
        try:
            title = driver.find_element(By.XPATH, '(//h2[@class="h2"]/span)[1]').text.strip()
        except:
            title = 'N/A'

        city = 'N/A'
        state = 'N/A'
        country = 'N/A'
        try:
            location = driver.find_element(By.XPATH, '//p[text()="Location:"]/preceding-sibling::h3').text
            if ',' in location:
                country=location.split('-') 
            else:   
                city=location
        except Exception as e:
            location = 'N/A'
            # print(f"An error occurred: {e}")

        if country == "Canada": pass
        source='barney.com'
        try:
            revenue=driver.find_element(By.XPATH, '//p[text()="Revenue:"]/preceding-sibling::h3').text.strip()
        except:
            revenue='N/A'
        try:
            cashflow=driver.find_element(By.XPATH, "//dt[contains(text(),'Cash Flow: ')]//following-sibling::dd/strong").text.strip()
        except:
            cashflow='N/A'

        try:
            inventory=driver.find_element(By.XPATH,'//div[contains(text(),"Inventory")]/following-sibling::div/text()')[0]
            inventory=''.join(inventory).strip()
        except:
            inventory='N/A'
        try:
            ebitda=driver.find_element(By.XPATH,'//p[text()="Seller’s Discretionary Earnings:"]/preceding-sibling::h3').text
        except:
            ebitda='N/A'
        try:
            description = driver.find_element(By.XPATH, '//h2[text()="Details:"]/following-sibling::p').text
        except:
            description='N/A'
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
            ask=driver.find_element(By.XPATH,'//p[text()="Asking Price:"]/preceding-sibling::h3').text
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

        data_tocsv=[title,city,state,country,url,industry,source,description,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
        save_to_csv(data_tocsv)

    except Exception as e:
        import traceback
        print(f"An error occurred while fetching data from {url}: {str(e)} \n")
        traceback_message = traceback.format_exc()
        print(traceback_message)
        driver.quit()

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

def main():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    # time.sleep(5)
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    driver.get("https://www.wearebarney.com/listed-now/")
    driver.maximize_window()
    time.sleep(4)
    urls=[]
    # Use WebDriverWait to wait for the element to be located
    filter_input=driver.find_element(By.XPATH,'//input[@id="minNetIncome"]')
    filter_input.send_keys(500000)
    btn=driver.find_element(By.XPATH,'//a[text()="Apply Filter"]')
    btn.click()
    time.sleep(7)
    for i in driver.find_elements(By.XPATH,'//a[text()="Learn More"]') :
            urls.append(i.get_attribute('href'))
    return urls

if __name__ == '__main__':
    urls=main()
    unique=set(urls)-set(last)
    for i in unique:
        fetch_data(i)
    update_first(unique)
