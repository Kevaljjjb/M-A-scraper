import  csv
import time
import re
import pytz
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from lxml import html

last_csv='./config/last_ana.csv'
last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)
    last = []

    for row in reader:
        last.append(row[0])
main_file='./output.csv'

base_url = "https://anabrokers.com/businesses-for-sale/"

def cashflow_revenue_checker(cash):
    if '$' in cash:
        # print(cash)
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        try:
            value = float(value)
        except:
            return False
        if value >= 2000000:
            return True
        else:
            return False
    else:
        return False

def fetch_data(driver,urls):
    for i in urls:
        try:
            # Get the page
            driver.get(i)
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="page_title"]')))
            try:
                title = driver.find_element(By.XPATH, '//div[@class="page_title"]').text.strip()
            except:
                title = 'N/A'

            city = 'N/A'
            state = 'N/A'
            country = 'N/A'
            try:
                location = driver.find_element(By.XPATH, '//span[text()="Location:"]/following-sibling::span').text
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    city=location
            except Exception as e:
                location = 'N/A'
            source='anabrokers.com'
            try:
                revenue=driver.find_element(By.XPATH, '//span[text()="Total Sales:"]/following-sibling::span').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//span[text()="Cash Flow:"]/following-sibling::span').text
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//strong[text()="Inventory:"]/..').text.replace("Inventory:","")
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//div[text()="Gross Income"]/following-sibling::div').text
            except:
                ebitda='N/A'
            try:
                desc=driver.find_elements(By.XPATH,'//div[text()="DESCRIPTION"]/../../../following-sibling::div[1]')
                # Extract text from each element
                description_texts = [element.text for element in desc]

                # Concatenate the text content
                description = ''.join(description_texts).strip()
            except:
                description='N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//h3[@class="text-center broker-name"]/strong').text
                listedby=''.join(listedby).strip()
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                element = driver.find_element(By.XPATH, '//p[@class="text-center"]')
                text_content = element.text
                lines = text_content.split('\n')
                for line in lines:
                    if 'Cell:' in line:
                        phone = line.split('Cell:')[1].strip()
                    elif 'Email:' in line:
                        mail = line.split('Email:')[1].strip()
                        
            except:
                phone='N/A'
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//span[text()="Industry:"]/following-sibling::span').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[text()="Price:"]/following-sibling::span').text
            except:
                ask='N/A'
            
            # code to get the date from the edt time
            # Get the current date and time in UTC
            current_datetime = datetime.now(pytz.utc)

            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)

            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%y")

            data_tocsv=[title,city,state,country,i,industry,source,description,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
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
            global new_count
            writer=csv.writer(f)
            writer.writerow(data)
            print(new_count)
            new_count+=1
            if new_count==1:
                update_first(data)

def  update_first(data):
     with open(last_csv,'w',newline='',encoding='utf-8')as f:
          w=csv.writer(f)
          for i in data:
            w.writerow(data) 

def main(driver):
    driver.get(base_url)
    time.sleep(2)
    urls=[]
    try:
        results=driver.find_elements(By.XPATH,'//div[@data-vc-full-width-init="true"]//div[@class="wpb_column vc_column_container vc_col-sm-4"]')
        for i in results:
            cf=i.find_element(By.XPATH,'.//div[contains(text(),"Cash Flow:")]/span').text
            bol=cashflow_revenue_checker(cf)
            link=i.find_element(By.XPATH,'. //a[text()="LEARN MORE »"]').get_attribute("href")
            if bol:
                if len(last)>0:
                    if last[4]==link:
                        raise Exception("Matched")
                else:
                    urls.append(link)
    except:
        print("Done")
    return urls

if __name__ =="__main__":
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    links=main(driver)
    fetch_data(driver,links)
    driver.close()


# //a[text()="LEARN MORE »"]