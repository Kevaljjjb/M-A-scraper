from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys 
import pytz
import time 
import re
import csv           

last_csv='./config/last_websitecloserv2.csv'

last=[]
last_count=0
with open(last_csv, 'r',encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for i in reader :
        last.append(i[0])

main_file="soft_data.csv"

def fetch_data(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(options=options)
    try:
         # Get the page
        driver.get(url)
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
            location = driver.find_element(By.XPATH, '//div//span[text()="Location:"]/../../following-sibling::div[1]').text.strip()
            if ',' in location:
                city,state=location.split(',')
            else:   
                city=location
        except Exception as e:
            location = 'N/A'
            print(f"An error occurred: {e}")

        print(city)
        source='Websitecloser.com'
        try:
            revenue=driver.find_element(By.XPATH, '//div//span[text()="Gross Revenue:"]/../../../following-sibling::div').text.strip()
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
            desc=driver.find_element(By.XPATH,'//div[@class="wysiwyg cfx"]//p').text
            decription=''.join(desc).strip()
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
            industry=driver.find_element(By.XPATH,'//div//span[text()="Category:"]/../../following-sibling::div[1]').text
        except:
            industry='N/A'
        try:
            ask=driver.find_element(By.XPATH,'//div[text()="Asking Price"]/following-sibling::div').text
        except:
            ask='N/A'
        driver.quit()
        
        # code to get the date from the edt time
        # Get the current date and time in UTC
        current_datetime = datetime.now(pytz.utc)

        # Convert to Eastern Daylight Time (EDT)
        eastern = pytz.timezone("US/Eastern")
        current_datetime_edt = current_datetime.astimezone(eastern)

        # Format the date as mm/dd/yy
        formatted_date = current_datetime_edt.strftime("%m/%d/%Y")
    

        data_tocsv=[title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
        save_to_csv(data_tocsv)

    except Exception as e:
        import traceback
        print(f"An error occurred while fetching data from {url}: {str(e)} \n")
        traceback_message = traceback.format_exc()
        print(traceback_message)
        driver.quit()

    return []
new_count=0
def save_to_csv(data):
        # with open('test_bizben.csv','a',newline='',encoding='utf-8')as f:
        #     writer=csv.writer(f)f
        #     writer.writerows(data)
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
     with open(last_csv,'a',newline='',encoding='utf-8')as f:
          global  first
          w=csv.writer(f)
          for i in data:
            w.writerow([i])  

def cashflow_revenue_checker(cash):
    if '$' in cash:
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        value = int(value)
        # print("cash Flow is :", cash)
        if value > 500000:            
            return True
        else :
            False
    else:
        return False  

def main():
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=Service(driver_path),options=options)
    urls=[]
    driver.get("https://www.websiteclosers.com/businesses-for-sale")
    time.sleep(2)

    scroll='window.scrollBy(0, 500);'
    driver.execute_script(scroll)
    time.sleep(5)
    try:
        driver.find_element(By.XPATH,'//li[@data-index="3"]')
    except:
        print("ola")
    js='''
            search=document.querySelector("input.s_name");
            search.click();
            const element = document.querySelector('li[data-index="3"]');
            element.click();
            '''
    driver.execute_script(js)
    # driver.send_keys
    time.sleep(3)
    break_count=0
    while True :
        try:
            driver.execute_script(scroll)
            results=driver.find_elements(By.XPATH,'//div[@class="post_content"]')
            # print(len(results))
            time.sleep(2)
            for result in results:
                href=result.find_element(By.XPATH,'.//a[text()="Details"]').get_attribute("href")
                cashflow=result.find_element(By.XPATH,'.//div[contains(text(),"Cash Flow")]/strong').text
                # print("Href is :",href," cashflow is :",cashflow)
                filter=cashflow_revenue_checker(cash=cashflow)
                if filter :
                    urls.append(href)
                else:
                    break_count+=1
                    break
            if break_count>= 100:
                break
            try:
                driver.find_element(By.XPATH,'(//a[@rel="next"])[1]').click()
                print("Next click")
                time.sleep(4)
            except:
                break
            
        except :
            break
    return urls

if __name__ == "__main__":
    hrefs =main()
    unique=set(hrefs)-set(last)
    for i in unique:
        fetch_data(i)