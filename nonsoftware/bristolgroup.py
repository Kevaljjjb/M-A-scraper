from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import re
import pytz
from datetime import datetime
import csv
import time

last_csv='./config/last_bristolegroup.csv'

last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)
    last = []

    for row in reader:
        last.append(row[0])

# Define the URL
main_file='./output.csv'
user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
def inner_page(data):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    global user_agent
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(options=options)
    # print("in the method and this is the data :",data)
    for i in data:
        url=i
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//h1[@class="co-name"]')))
            try:
                title=driver.find_element(By.XPATH,'//h1[@class="co-name"]').text
                title=''.join(title.strip())
            except:
                title='N/A'

            city='N/A'
            state='N/A'
            country='N/A'


            try:
                location = driver.find_element(By.XPATH,'//h3[@class="city-state"]').text
                # city=location

                if ',' in location:
                    city,state=location.split(',')
                else:   
                    country=location
            except Exception as e:
                location = 'N/A'
                # print(f"An error occurred: {e}")



            # print(city)
            source='bristolegroup.com'
            try:
                revenue=driver.find_element(By.XPATH,'//span[contains(text(),"Revenue:")]/..').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH,'//span[contains(text(),"Cash Flow:")]/..').text
            except:
                cashflow='N/A'
            try:
                inventory=driver.find_element(By.XPATH,'//span[contains(text(),"Inventory:")]/..').text
                inventory=''.join(inventory).strip()
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//div[@class="grid grid--6"]/p[contains(text(),"EBITDA")]/../following-sibling::div').text
            except:
                ebitda='N/A'
                                
            try:
                desc=driver.find_element(By.XPATH,'//h2[contains(text(),"Overview")]/following-sibling::p').text
                description = ''.join(desc).strip()
                
            except:
                description='N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//li[@class="name"]').text
            except:
                listedby='N/A'
            listedby_firm='N/A'
            try:
                phones = driver.find_elements(By.XPATH, '//li[@class="phone"]')
                # Collect text from each element and join them with '/'
                phone_texts = [phone.text for phone in phones]
                phone = '/'.join(phone_texts).strip()
            except:
                phone='N/A'
            try:
                mail=driver.find_element(By.XPATH,'//li[@class="email"]/a').text
            except:
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'')
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[contains(text(),"Price:")]/..').text
            except:
                ask='N/A'

            try:
                listed_date=driver.find_element(By.XPATH,'')
            except:
                listed_date=''
            # code to get the date from the edt time
            # Get the current date and time in UTC
            current_datetime = datetime.now(pytz.utc)
            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)
            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")


            data_to_save = [title, city, state, country, url, industry, source, description, listedby_firm, listedby, phone, mail, ask, revenue, cashflow, inventory, ebitda, formatted_date]
            # prsata_to_save)
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
    with open(last_csv, 'a', newline='', encoding='utf-8') as f:
        # global first
        w = csv.writer(f)
        for i in data:
            w.writerow([i])

def main():
    # Set up Chrome WebDriver
    option=webdriver.ChromeOptions()
    option.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=option)
    # Navigate to the URL
    url = "https://www.bristolgrouponline.com/buy-a-business/page/1/#search"
    driver.get(url)
    try:
        js='''
            // Find the checkbox element by its ID
            var checkbox = document.getElementById("min-1M");

            // Check the checkbox
            if (checkbox) {
                checkbox.checked = true;
            }

            // Find the button element by its attributes
            var button = document.querySelector('button[name="search"].search');

            // Click the button
            if (button) {
                button.click();
            }
        '''
        driver.execute_script(js)
        time.sleep(3)
        lis=driver.find_elements(By.XPATH,'//div[@class="result-block"]')
        data=[]
        for li in lis:
            # industry=li.get_attribute('data-industry')
            try:
                cashfl=li.find_element(By.XPATH,'.//span[contains(text(),"Cash Flow")]/..').text
                cashflow= re.sub(r"[^\d\-+\.]", "", cashfl)
                cashflow=int(cashflow)
                # ask=li.find_element(By.XPATH,'./p[@class="price"]/span[2]/strong').text
                try:
                    url=li.find_element(By.XPATH,'.//a[contains(text(),"More Info")]').get_attribute('href')
                    print(cashflow,url)
                except Exception as e:
                    print(str(e))
                    url=''
            except:
                cashflow=None
                cashfl=''


            if cashflow != None:
                if cashflow >=2000000:
                    data.append(url)
        return data
    finally:
        driver.quit()

if __name__ == "__main__":
    all_url=main()
    unique=set(all_url)-set(last)
    if len(unique) >0 :
        inner_page(list(unique))
        update_first(list(unique))


