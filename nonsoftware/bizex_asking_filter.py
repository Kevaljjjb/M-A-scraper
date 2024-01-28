from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pytz
import time 
import re
import csv        


last_csv='./config/last_bizex.csv'

last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader, None)
    for i in reader :
        last.append(i[0])

main_file="output.csv"

def fetch_data(urls):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
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
            state = 'N/A'
            country = 'N/A'
            try:
                location = driver.find_element(By.XPATH, '//th[text()="General Location:"]/following-sibling::td').text
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    city=location
            except Exception as e:
                location = 'N/A'
            source='bizex.net'
            try:
                revenue=driver.find_element(By.XPATH, '//th[text()="Gross Sales:"]/following-sibling::td').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//th[text()="Discretionary Cash Flow:"]/following-sibling::td').text
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//th[text()="Inventory:"]/following-sibling::td').text
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//div[text()="Gross Income"]/following-sibling::div').text
            except:
                ebitda='N/A'
            try:
                decription=''
                for i in driver.find_elements(By.XPATH,'(//p[not(node())])[1]/following-sibling::p[not(text()="Services include;")]'):
                    decription+=i.text
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
                mail=driver.find_element(By.XPATH,'//i[@class="fa fa-envelope-o"]/following-sibling::a').text
            except:
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//div[@data-id="fb459aa"]').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//th[text()="Asking Price:"]/following-sibling::td').text
            except:
                ask='N/A'

            text = driver.find_element(By.XPATH,'(//div[@class="broker-photo hidden-xs hidden-sm"]/following-sibling::p)[1]').get_attribute('innerHTML')

            # Extracting the data using regular expressions
            try:
                listedby = re.search(r"<b>(.*?)</b>", text).group(1)
            except AttributeError:
                listedby = "Name not found"

            try:
                cell=driver.find_element(By.XPATH,'(//div[@class="broker-photo hidden-xs hidden-sm"]/following-sibling::p)[1]').text
                phone += "Ofice : "+cell.split("Office: ")[1].split("\nLic#:")[0]
            except AttributeError:
                phone = "Office number not found"
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

def asking_checker(ask):
    if '$' in ask:
        value = re.sub(r"[^\d\-+\.]", "", ask)
        # Convert the value to a float.
        value = int(value)
        # print("cash Flow is :", cash)
        if value > 6000000:            
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
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    driver.get("https://www.bizex.net/business-for-sale")
    
    while True:
        results=driver.find_elements(By.XPATH,'//div[@class="listing clearfix"]')
        for result in results:
            try:
                value=result.find_element(By.XPATH,'.//p[@class="financials"]').text
                price=value.split("Gross Sales:\n")[0].replace("Asking Price:\n",'')
                cashflow=value.split("Cash Flow:\n")[1]
                revenue=value.split("Gross Sales:\n")[1].split("Cash Flow:\n")[0]
            except Exception as e:
                print(str(e))
                cashflow=''
                revenue=''
                price=''
            if '$' not in cashflow and '$' not in revenue and '$' in price and asking_checker(price):
                url=result.find_element(By.XPATH,'.//a[text()="View Full Listing"]')
                urls.append(url.get_attribute('href'))
        try:
            driver.find_element(By.XPATH,'//a[text()="Next >"]').click()
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