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


last_csv='./config/last_thefirm.csv'
last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)

    for row in reader:
        last.append(row[0])

# Define the URL
main_file='test_data.csv'
def inner_page(data):
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    # print("in the method and this is the data :",data)
    for i in data:
        url=i[0]
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//h2[@class="listing-title"]')))
            try:
                title=driver.find_element(By.XPATH,'//h2[@class="listing-title"]').text
                title=''.join(title.strip())
            except:
                title='N/A'

            city='N/A'
            state='N/A'
            country='N/A'

            try:
                location = driver.find_element(By.XPATH,'//span[contains(text(),"Location")]/following-sibling::span').text
                # city=location
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    city=location
            except Exception as e:
                location = 'N/A'
            source='thefirmadv.com'
            try:
                revenue=driver.find_element(By.XPATH,'//span[contains(text(),"Revenue")]/following-sibling::span').text
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
                ebitda=driver.find_element(By.XPATH,"//b[contains(text(),'EBITDA:')]/following-sibling::b[1]/text()").text
            except:
                ebitda='N/A'
                                
            try:
                desc=driver.find_element(By.XPATH,'//section[@class="bi-description"]').text
                description=''.join(desc).strip()
            except:
                description='N/A'
            listedby='N/A'
            listedby_firm='N/A'
            phone='N/A'
            mail='N/A'
            try:
                industry=i[1]
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[contains(text(),"Price")]/following-sibling::span').text
            except:
                try:
                    ask=i[2]
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
    with open(last_csv, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        for i in data:
            w.writerow([i])
def cashflow_revenue_checker(cash):
    if '$' in cash:
        value = re.sub(r"[^\d\-+\.]", "", cash)
        try:
            value = int(value)
        except:
            return False
        if value >= 2000000:
            return True
        else:
            return False  # You were missing the return statement here
    else:
        return False
def main():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    # Navigate to the URL
    url = "https://thefirmadv.com/business-buyer/opportunities/"
    driver.get(url)
    try:
        button_label = driver.find_element(By.XPATH, '//label[@for="filter-option4"]')
        button_label.click()

        # Wait for the element to become available
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.XPATH, '//ul[@class="filtered-listings top-level-listings"]/li')))
        wait.until(EC.presence_of_element_located((By.XPATH, '//em[@class="please-wait"]')))
        wait.until(EC.invisibility_of_element_located((By.XPATH, '//em[@class="please-wait"][@style="display: none;"]')))
        time.sleep(3)
        lis=driver.find_elements(By.XPATH,'//ul[@class="filtered-listings top-level-listings"]/li')
        data=[]
        for li in lis:
            industry=li.get_attribute('data-industry')
            try:
                cashflow=li.find_element(By.XPATH,'./p[@class="price"]/span[2]/strong').text
                ask=li.find_element(By.XPATH,'./p[@class="price"]/span[2]/strong').text
                try:
                    url=li.find_element(By.XPATH,'./h4/a').get_attribute('href')
                except Exception as e:
                    print(str(e))
                    url=''
            except:
                cashflow=None

            if cashflow != None:
                if cashflow_revenue_checker(cashflow):
                    data.append([url, industry,ask])
        if len(data) >0:
            return data
    except Exception as e:
        print(str(e))
        exit()
    finally:
        driver.quit()

if __name__ == "__main__":
    links=main()
    unique=[item for item in links if item[0] not in last]
    print(unique)
    if len(unique) >0:
        inner_page(unique)
        update_first([i[0] for i in unique])



