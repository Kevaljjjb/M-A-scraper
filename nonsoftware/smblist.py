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


last_csv='./config/last_smblist.csv'

last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader, None)
    for i in reader :
        last.append(i[0])

main_file="output.csv"

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
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
            try:
                title = driver.find_element(By.XPATH, '//h1').text
            except:
                title = 'N/A'

            city = 'N/A'
            state = 'N/A'
            country = 'N/A'
            

            print(city)
            source='thesmblist.com'
            try:
                revenue=driver.find_element(By.XPATH, '//p[contains(text(),"Revenue: ")]').text.replace("Revenue: ","")
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//p[contains(text(),"Cashflow: ")]').text.replace("Cashflow: ","")
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//div[contains(text(),"Inventory")]/following-sibling::div/text()')[0]
                inventory=''.join(inventory).strip()
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//p[contains(text(),"Ebitda: ")]').text.replace("Ebitda: ","")
            except:
                ebitda='N/A'
            try:
                decription=''
                for i in driver.find_elements(By.XPATH,'//p[not(node())]/following-sibling::p[not(contains(text(),"Link to deal"))]'):
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
                ask=driver.find_element(By.XPATH,'//p[contains(text(),"Price: ")]').text.replace("Price: ",'')
            except:
                ask='N/A'
            try:
                sourcelink=driver.find_element(By.XPATH,'//a[text()="here"]').get_attribute('href')
            except:
                sourcelink=''
            current_datetime = datetime.now(pytz.utc)

            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)

            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")
            if driver.current_url not in last:

                if '$' in cashflow:
                    if cashflow_revenue_checker(cashflow) :
                        data_tocsv=[title,city,state,country,driver.current_url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date,'','',sourcelink]
                        save_to_csv(data_tocsv)
                        update_first(driver.current_url)
                elif '$' in ebitda:
                    if cashflow_revenue_checker(ebitda):
                        data_tocsv=[title,city,state,country,driver.current_url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date,'','',sourcelink]
                        save_to_csv(data_tocsv)
                        update_first(driver.current_url)
                else :
                    pass

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
            w.writerow([data])  

def main():
    urls=[]
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    driver.get("https://thesmblist.com/free-listings/")
    results=driver.find_elements(By.XPATH,'//td[@class="dtr-control"]//a')
    for result in results:
        urls.append(result.get_attribute('href'))
    return urls


if __name__ == "__main__":
    urls=main()
    fetch_data(urls)


# https://latonas.com/listings/?result_sorting_order=&result_sorting_quantity=50&broker=any&price_range=any&revenue_range=500000%2B&unique_range=any&profit_range=any&searchTags=&location=US