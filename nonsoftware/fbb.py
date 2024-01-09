import requests
from lxml import html
import  csv
import time
import concurrent.futures
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

last_csv='./config/last_fbb.csv'
last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)
    last = []

    for row in reader:
        last.append(row[0])


# Define the URL
main_file='output.csv'
base_url = "https://www.fbb.com/businesses-for-sale/"

def cashflow_revenue_checker(cash):
    if '$' in cash:
        # print(cash)
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        try:
            value = float(value)
        except:
            return False
        if value >= 4000000:
            return True
        else:
            return False  # You were missing the return statement here
    else:
        return False
    
def fetch_data(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    try:
         # Get the page
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        title = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@style="color: #005d9d;"]')))
        try:
            title = driver.find_element(By.XPATH, '//span[@style="color: #005d9d;"]').text.strip()
        except:
            title = 'N/A'

        city = 'N/A'
        state = 'N/A'
        country = 'N/A'
        try:
            location = driver.find_element(By.XPATH, '//strong[text()="Location: "]/../..').text.replace("Location: ","")
            if ',' in location:
                city,state=location.split(',')
            else:   
                city=location
        except Exception as e:
            location = 'N/A'
            print(f"An error occurred: {e}")

        # print(city)
        source='fbb.com'
        try:
            revenue=driver.find_element(By.XPATH, '//span[text()="Gross Revenue: "]/../following-sibling::span').text
        except:
            revenue='N/A'
        try:
            cashflow=driver.find_element(By.XPATH, "//dt[contains(text(),'Cash Flow: ')]//following-sibling::dd/strong").text.strip()
        except:
            cashflow='N/A'

        try:
            inventory=driver.find_element(By.XPATH,'//div[contains(text(),"Inventory")]/following-sibling::div/text()')[0]
            inventory=''.join(inventory).strip()
        except:
            inventory='N/A'
        try:
            ebitda=driver.find_element(By.XPATH,"//span[text()='Adjusted Profit: ']/../..").text.replace("Adjusted Profit: ","")
        except:
            ebitda='N/A'
        try:
            desc=driver.find_element(By.XPATH,'//td[img]/../following-sibling::tr[1]//p').text
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
            industry=driver.find_element(By.XPATH,'//strong[text()="Industries: "]/../..').text.replace("Industries: ","")
        except:
            industry='N/A'
        try:
            ask=driver.find_element(By.XPATH,'//strong[text()="Asking Price:"]/../following-sibling::span').text
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
            writer=csv.writer(f)
            writer.writerow(data)


def  update_first(data):
     with open(last_csv,'a',newline='',encoding='utf-8')as f:
          w=csv.writer(f)
          for i in data:
            w.writerow([i])  
    
def inside_page(urls):

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks for each URL and collect the results
            executor.map(fetch_data, urls)

def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    driver.get(base_url)
    data = []
    while True :
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "listings-frame"))
            )
            driver.switch_to.frame(iframe)
            
            # Use XPath to find elements in the parsed HTML
            results = driver.find_elements(By.XPATH, "//ul[@class='listings']/li")
            # print(results)
            for i in results:
                rev = i.find_element(By.XPATH, ".//strong[text()='GROSS REVENUE: ']/..").text
                bol = cashflow_revenue_checker(rev)
                # print(rev)
                if bol:
                    url = i.find_element(By.XPATH, ".//a[contains(text(),'MORE INFO >>')]")
                    ask =i.find_element(By.XPATH, "//span[contains(text(),'ASKING PRICE: ')]/following-sibling::span").text
                    data.append(url.get_attribute("href"))

            # Switch back to the default content before clicking the next page
            # driver.switch_to.default_content()
            try:
                driver.find_element(By.XPATH, '//a[@class="next_page"]').click()
                time.sleep(2)
                driver.switch_to.default_content()
                time.sleep(2)
            except:
                print("No Next button")
                break
            return data
        except:
            return data


if __name__== "__main__":
    allhrefs=main()
    unique=set(allhrefs)-set(last)
    if len(unique)>0:
        inside_page(unique)
        update_first(list(unique))
