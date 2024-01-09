from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pytz
from datetime import datetime
import csv
import time


last_csv='./config/last_dealforce.csv'
last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader)

    for row in reader:
        last.append(row[0])

# Define the URL
main_file='output.csv'
global user_agent
user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'

def fetch_data(data):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    # print("in the method and this is the data :",data)
    for i in data:
        url=i
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="blog-single-header"]/h1')))
            try:
                title=driver.find_element(By.XPATH,'//div[@class="blog-single-header"]/h1').text
                title=''.join(title.strip())
            except:
                title='N/A'

            city='N/A'
            state='N/A'
            country='N/A'


            try:
                location = driver.find_element(By.XPATH,'//div[@class="grid grid--6"]/p[contains(text(),"Region")]/../following-sibling::div').text
                # city=location
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    country=location
            except Exception as e:
                location = 'N/A'
            # print(city)
            source='dealforce.com'
            try:
                revenue=driver.find_element(By.XPATH,'//div[@class="grid grid--6"]/p[contains(text(),"Revenue")]/../following-sibling::div').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH,'//span[contains(text(),"Cash Flow")]/following-sibling::span').text
            except:
                cashflow='N/A'
            try:
                inventory=driver.find_element(By.XPATH,'//span[contains(text(),"Inventory")]/following-sibling::span').text
                inventory=''.join(inventory).strip()
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//div[@class="grid grid--6"]/p[contains(text(),"EBITDA")]/../following-sibling::div').text
            except:
                ebitda='N/A'     
            try:
                desc=driver.find_elements(By.XPATH,'//div[@class="blog-single__content"]/p')
                description = '\n'.join([i.text.strip() for i in desc])
            except:
                description='N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//div[@class="grid grid--6 grid--border"]/p[2]').text
            except:
                listedby='N/A'
            listedby_firm='N/A'
            try:
                phone=driver.find_element(By.XPATH,'//div[@class="grid grid--6 grid--border"]/p[3]').text
            except:
                phone='N/A'
            try:
                mail=driver.find_element(By.XPATH,'//div[@class="grid grid--6 grid--border"]/p[4]').text
            except:
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'')
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[contains(text(),"Price")]/following-sibling::span').text
            except:
                ask='N/A'
            current_datetime = datetime.now(pytz.utc)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

            data_to_save = [title, city, state, country, url, industry, source, description, listedby_firm, listedby, phone, mail, ask, revenue, cashflow, inventory, ebitda, formatted_date]
            save_to_csv(data_to_save)
        except Exception as e:
            import traceback 
            print(f"An error occurred while fetching data from {url}: {str(e)}")
            traceback_message = traceback.format_exc()
            print(traceback_message)
    driver.quit()


def save_to_csv(data):
    with open(main_file, 'a', newline='', encoding='utf-8') as f:
        if len(data[0]) > 0:
            writer = csv.writer(f)
            writer.writerow(data)

def update_first(data):
    with open(last_csv,'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        for i in data:
            w.writerow([i])
def cashflow_revenue_checker(rev):
    if '$' in rev:
        # print(rev)
        value = re.sub(r"[^\d\-+\.]", "", rev)
        # Convert the value to a float.
        try:
            value = float(value)
        except:
            return False
        if value >= 2000000:
            return True
        else:
            return False  # You were missing the return statement here
    else:
        return False
    
def main():
    # Set up Chrome WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    url = "https://www.dealforce.com/mergers-and-acquisitions/all/for-sale"
    driver.get(url)

    try:
        time.sleep(3)
        lis=driver.find_elements(By.XPATH,'//div[@class="grid grid--4 grid--merger"]')
        data=[]
        for li in lis:
            try:
                cashfl=li.find_element(By.XPATH,'.//li[contains(text(),"EBITDA")]/span').text
                # ask=li.find_element(By.XPATH,'./p[@class="price"]/span[2]/strong').text
                try:
                    url=li.find_element(By.XPATH,'.//a[contains(text(),"View Details")]').get_attribute('href')
                except Exception as e:
                    print(str(e))
                    url=''
                # print(url, industry)
            except:
                cashfl=''
            if cashflow_revenue_checker(cashfl):
                    data.append(url)
        return data
    finally:
        driver.quit()

if __name__ == "__main__": 
    allhref=main()
    unique=set(allhref)-set(last)
    if len(unique)>0:
        fetch_data(unique)
        update_first(unique)

# price - //ul[@class="filtered-listings top-level-listings"]/li/p[@class="price"]/span[2]/strong
# href  -  /li/h4/a


