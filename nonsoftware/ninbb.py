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

last_csv='./config/last_ninbb.csv'

last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader, None)
    for i in reader :
        last.append(i[0])

main_file="output.csv"

def fetch_data(urls):
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    driver.maximize_window()
    time.sleep(2)
    for i in urls:
        try:
            # Get the page
            driver.get(i)
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="section-title"]/h3')))
            try:
                title = driver.find_element(By.XPATH, '//div[@class="section-title"]/h3').text.strip()
            except:
                title = 'N/A'

            city = 'N/A'
            state = 'N/A'
            country = 'N/A'
            try:
                location = driver.find_element(By.XPATH, '//div[@class="section-title"]/strong').text
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    city=location
            except Exception as e:
                location = 'N/A'

            source='ninbb.com'
            try:
                revenue=driver.find_element(By.XPATH,'//span[contains(text(),"Gross Revenue ")]/following-sibling::span').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH,'//span[contains(text(),"Cash Flow ")]/following-sibling::span').text.strip()
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//span[contains(text(),"Inventory ")]/following-sibling::span').text
                inventory=''.join(inventory).strip()
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//span[contains(text(),"EBITDA")]/following-sibling::span').text
            except:
                ebitda='N/A'
            try:
                business_description_element = driver.find_element(By.XPATH,"//h2[text()='Business Description']")
                detail_information_element = driver.find_element(By.XPATH,"//h2[text()='Detail Information']")

                # Use JavaScript to extract the content between these two elements
                decription = driver.execute_script("""
                    var startElement = arguments[0];
                    var endElement = arguments[1];
                    var range = document.createRange();
                    range.setStartAfter(startElement);
                    range.setEndBefore(endElement);
                    return range.cloneContents().textContent;
                """, business_description_element, detail_information_element)
                decription=decription.strip()
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
                industry=driver.find_element(By.XPATH,'//div[@data-id="fb459aa"]').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[contains(text(),"Asking Price")]/following-sibling::span').text
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

def main():
    urls=[]
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    driver.get("https://www.ninbb.com/businesses-for-sale.php")
    results=driver.find_elements(By.XPATH,'//div[@class="bottom"]')
    for result in results:
        revenue=result.find_element(By.XPATH,'.//span[text()="Cash Flow"]/following-sibling::span').text
        if cashflow_revenue_checker(revenue):
            url=result.find_element(By.XPATH,'.//a[contains(text(),"Click here for more information")]')
            urls.append(url.get_attribute('href'))
    return urls


if __name__ == "__main__":
    urls=main()
    unique=set(urls)-set(last)
    if len(unique) >0:
        fetch_data(unique)  
        update_first(unique)