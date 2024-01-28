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


last_csv='./config/last_appbusinessbroker.csv'

last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader, None)
    for i in reader :
        last.append(i[0])

main_file="soft_data.csv"

def fetch_data(urls):
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
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
            

            print(city)
            source='appbusinessbroker.com'
            try:
                revenue=driver.find_element(By.XPATH, '//h2[text()="Revenue:"]/../../../../following-sibling::div[1]').text.strip()
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, "//div[text()='Cash Flow']/following-sibling::div").text.strip()
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//div[contains(text(),"Inventory")]/following-sibling::div/text()')[0]
                inventory=''.join(inventory).strip()
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//div[text()="Gross Income"]/following-sibling::div').text
            except:
                ebitda='N/A'
            try:
                decription=driver.find_element(By.XPATH,'//h2[text()="Description"]/../../../../following-sibling::div[1]').text
            except:
                decription='N/A'
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
                industry=driver.find_element(By.XPATH,'//div[@data-id="fb459aa"]').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//h2[text()="Price:"]/../../../../following-sibling::div[1]').text
            except:
                ask='N/A'
            current_datetime = datetime.now(pytz.utc)

            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)

            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

            data_tocsv=[title,city,state,country,i,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
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
def cashflow_revenue_checker(rev):
    if '$' in rev:
        value = re.sub(r"[^\d\-+\.]", "", rev)
        # Convert the value to a float.
        value = int(value)
        # print("cash Flow is :", cash)
        if value > 1000000:            
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
    driver.get("https://www.appbusinessbrokers.com/buy/")
    driver.maximize_window()
    time.sleep(8)

    method='''
    function scrollToPageBottom() {
        window.scrollTo(0, document.body.scrollHeight);
    }
    scrollToPageBottom();
    '''
    # driver.execute_script(filter)
    time.sleep(3)
    for _ in  range(7): #here _ indicates that variable in tbe loop is not gonna be used
        driver.execute_script(method)
        time.sleep(2)
    time.sleep(2)


    results=driver.find_elements(By.XPATH,'//div[@data-post-id]')
    for result in results:
        href =result.find_element(By.XPATH,'.//a[contains(@class,"elementor-button-link")]').get_attribute("href")
        rev=result.find_element(By.XPATH,'.//h2[text()="Revenue:"]/../../../../following-sibling::div[1]').text
        print(rev)
        # check for the revenue
        if cashflow_revenue_checker(rev):
            urls.append(href)
    return urls


if __name__ == "__main__":
    urls=main()
    unique=set(urls)-set(last)
    print(len(unique))
    fetch_data(unique)
    update_first(unique)