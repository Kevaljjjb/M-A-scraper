import  csv
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pytz
import time

mainfile="output.csv"
last_csv='./config/last_summitacquisitions.csv'
last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    last = []

    for row in reader:
        last.append(row[0])
def fetch_data(driver):
    try:
        try:
            title = driver.find_element(By.XPATH, './h2').text
        except:
            title = 'N/A'

        city = 'N/A'
        state = 'N/A'
        country = 'N/A'
        try:
            location = driver.find_element(By.XPATH, '//th[text()="Location"]/following-sibling::td').text
            if ',' in location:
                country,state=location.split(',')
            else:   
                state=location
        except Exception as e:
            location = 'N/A'

        # print(city)
        source='summitacqusitions.com'
        try:
            revenue=driver.find_element(By.XPATH, './p[1]').text.split("Revenue Range:")[1].split("EBITDA Range:")[0].replace("\n",'')
        except:
            revenue='N/A'
        try:
            cashflow=driver.find_element(By.XPATH, '//th[text()="Cash Flow"]/following-sibling::td').text
        except:
            cashflow='N/A'

        try:
            inventory=driver.find_element(By.XPATH,'//th[text()="Inventory"]/following-sibling::td').text
        except:
            inventory='N/A'
        try:
            ebitda=driver.find_element(By.XPATH, './p[1]').text.split("EBITDA Range:")[1].replace("\n",'')
        except:
            ebitda='N/A'
        try:
            description=driver.find_element(By.XPATH,'./p[2]').text.replace("More Information.",'').replace("Description:\n",'')
        except:
            description = 'N/A'
        try:
            listedby=driver.find_element(By.XPATH,'//a[@class="borkerLink"]').text
        except:
            listedby='N/A'
        try:
            listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
            listedby_firm=''.join(listedby_firm).strip()
        except:
            listedby_firm='N/A'
        try:
            main_phone=driver.find_element(By.XPATH,'//label[contains(text(),"Phone:")]/..').text
            mobile=driver.find_element(By.XPATH,'//label[contains(text(),"Mobile:")]/..').text
            phone=main_phone+"\n"+mobile
                    
        except:
            phone='N/A'
        try:
            mail=driver.find_element(By.XPATH,'./h2//a').get_attribute('href').split("?")[0].replace("mailto:","")
        except:
            mail='N/A'
        try:
            industry=driver.find_element(By.XPATH,'./p[1]').text.split("Revenue Range:")[0].replace("Industry:",'')
        except:
            industry='N/A'
        try:
            ask=driver.find_element(By.XPATH,'//h5[contains(text(),"Asking Price: ")]').text.replace("Asking Price: ","")
        except:
            ask='N/A'
        
        # code to get the date from the edt time
        # Get the current date and time in UTC
        current_datetime = datetime.now(pytz.utc)

        # Convert to Eastern Daylight Time (EDT)
        eastern = pytz.timezone("US/Eastern")
        current_datetime_edt = current_datetime.astimezone(eastern)

        # Format the date as mm/dd/yy
        formatted_date = current_datetime_edt.strftime("%m/%d/%Y")
        if description not in last:
            data_tocsv=[title,city,state,country,"https://summitacquisitions.com/buyers-seeking-companies/",industry,source,description,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
            save_to_csv(data_tocsv)
            update_first(description)

    except Exception as e:
        import traceback
        print(f"An error occurred while fetching data from: {str(e)} \n")
        traceback_message = traceback.format_exc()
        print(traceback_message)

def save_to_csv(data):
    with open(mainfile,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            global new_count
            writer=csv.writer(f)
            writer.writerow(data)

def  update_first(data):
     with open(last_csv,'a',newline='',encoding="utf-8")as f:
            w=csv.writer(f)
            w.writerow([data])    

def cashflow_revenue_checker(cash):
    if '$' in cash:
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        value = float(value)
        # print("cash Flow is :", cash)
        if value > 2.0:            
            return True
        else :
            False
    else:
        return False  

def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    wait = WebDriverWait(driver, 10)
    urls=[]
    driver.get('https://summitacquisitions.com/buyers-seeking-companies/')
    time.sleep(3)
    while True:
        trs = driver.find_elements(By.XPATH, '//table[@style="width: 100%;"]//tr/td')
        for tr in trs:
            cf=tr.find_element(By.XPATH,'./p[1]').text.split("EBITDA Range:")[1].split("to ")[1]
            if cashflow_revenue_checker(cf):
                fetch_data(tr)
        break
    return urls

if __name__ == "__main__":
    main()
