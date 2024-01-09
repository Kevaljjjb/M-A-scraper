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

last_csv='./config/last_benjamingroup.csv'

last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)

    for row in reader:
        last.append(row[0])

def cashflow_revenue_checker(cash):
    if '$' in cash:
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        value = int(value)
        print("cash Flow is :", cash)
        if value > 2000000:            
            return True
        else :
            False
    else:
        return False  

main_file='output.csv'
titles=[]
user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
def main():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    global user_agent
    time.sleep(5)
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    driver.get("https://www.benjaminrossgroup.com/businesses-for-sale")
    data=driver.find_elements(By.XPATH,'//ul[@class="business-listings"]/li')
    # print("in the method and this is the data :",data)
    
    for i in data:
        try:
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, './/h3')))
            try:
                title=i.find_element(By.XPATH,'.//h3').text
                title=''.join(title.strip())
            except:
                title='N/A'
            
            city='N/A'
            state='N/A'
            country='N/A'


            try:
                location = i.find_element(By.XPATH,'.//h4[contains(text(),"Location:")]/following-sibling::span').text
                # city=location

                if ',' in location:
                    city,state=location.split(',')
                else:   
                    country=location
            except Exception as e:
                location = 'N/A'
                # print(f"An error occurred: {e}")


            source='benjamingroup.com'
            try:
                revenue=i.find_element(By.XPATH,'.//h4[contains(text(),"Gross Revenue:")]/following-sibling::span').text
            except:
                revenue='N/A'
            try:
                cashflow=i.find_element(By.XPATH,'.//h4[contains(text(),"Cash Flow:")]/following-sibling::span').text
            except:
                cashflow='N/A'
            try:
                inventory=i.find_element(By.XPATH,'.//span[contains(text(),"Inventory:")]/..').text
                inventory=''.join(inventory).strip()
            except:
                inventory='N/A'
            try:
                ebitda=i.find_element(By.XPATH,'.//div[@class="grid grid--6"]/p[contains(text(),"EBITDA")]/../following-sibling::div').text
            except:
                ebitda='N/A'
                                
            try:
                desc=i.find_element(By.XPATH,'.//div[@class="the-content"]').text
                description = ''.join(desc).strip()
                
            except:
                description='N/A'
            try:
                listedby=i.find_element(By.XPATH,'.//div[@class="grid grid--6 grid--border"]/p[2]').text
            except:
                listedby='N/A'
            listedby_firm='N/A'
            try:
                phone=i.find_element(By.XPATH,'.//div[@class="grid grid--6 grid--border"]/p[3]').text
            except:
                phone='N/A'
            try:
                mail=i.find_element(By.XPATH,'.//div[@class="grid grid--6 grid--border"]/p[4]').text
            except:
                mail='N/A'
            try:
                industry=i.find_element(By.XPATH,'cfghh')
            except:
                industry='N/A'
            try:
                ask=i.find_element(By.XPATH,'.//h4[contains(text(),"Price:")]/following-sibling::span').text
            except:
                ask='N/A'
            current_datetime = datetime.now(pytz.utc)
            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)
            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

            if description not in last:                    
                if cashflow_revenue_checker(cashflow):
                    data_to_save = [title, city, state, country, driver.current_url, industry, source, description, listedby_firm, listedby, phone, mail, ask, revenue, cashflow, inventory, ebitda, formatted_date]
                # prsata_to_save)
                    save_to_csv(data_to_save)
                    update_first(description)
            else:
                print("")
                

        except Exception as e:
            import traceback 
            print(f"An error occurred while fetching data from {driver.current_url}: {str(e)}")
            traceback_message = traceback.format_exc()
            print(traceback_message)
    driver.quit()


def save_to_csv(data):
    with open(main_file, 'a', newline='', encoding='utf-8') as f:
        if len(data[0]) > 0:
            writer = csv.writer(f)
            writer.writerow(data)

def update_first(i):
    with open(last_csv, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([i])
if __name__ == "__main__":
    main()
    unique=set(titles)-set(last)
    