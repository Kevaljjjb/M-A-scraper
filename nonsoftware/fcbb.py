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


last_csv='./config/last_fcbb.csv'
last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    last = []
    next(reader)

    for row in reader:
        # print(row)
        last.append(row[0])

# Define the URL
main_file='output.csv'
base_url = "https://fcbb.com/businesses-for-sale?page=1&pagesize=1000&sort=ListingDateNewerToOlder&filter=All"

def fetch_data(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        title = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="dmRespCol large-12 medium-12 small-12 u_1140889450"]/div[@style="transition: none 0s ease 0s; text-align: left; display: block;"][1]')))
        try:
            title = driver.find_element(By.XPATH, '//div[@class="dmRespCol large-12 medium-12 small-12 u_1140889450"]/div[@style="transition: none 0s ease 0s; text-align: left; display: block;"][1]').text.strip()
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
        source='fcbb.com'
        try:
            revenue=driver.find_element(By.XPATH, '//div//span[text()="Gross Revenue:"]/../../../following-sibling::div').text.strip()
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
            ebitda=driver.find_element(By.XPATH,"//b[contains(text(),'EBITDA:')]/following-sibling::b[1]/text()")[0]
        except:
            ebitda='N/A'
        try:
            desc=driver.find_element(By.XPATH,'//div[@class="dmRespCol large-12 medium-12 small-12 u_1140889450"]/div[4]').text
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
            ask=driver.find_element(By.XPATH,'//div//span[text()="Listed Price:"]/../../../following-sibling::div').text
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
                
def save_to_csv(data):
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            writer=csv.writer(f)
            writer.writerow(data)
            

def  update_first(data):
     with open(last_csv,'a',newline='',encoding='utf-8')as f:
          w=csv.writer(f)
        #   w.writerow(headers)
          for i in data:
            w.writerow([i])  
    
def inside_page(urls):

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks for each URL and collect the results
            executor.map(fetch_data, urls)

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
unmatched=0
def main_page(url,driver):
    # Navigate to the URL
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    select_element = wait.until(EC.presence_of_element_located((By.ID, 'inputSortBy')))
    time.sleep(4)
    js='''// Find the select element by its ID
        var selectElement = document.getElementById("inputSortBy");

        // Set the value of the select element to "PriceHighToLow"
        selectElement.value = "PriceHighToLow";

        // Create a change event to trigger the selection change
        var event = new Event("change", { bubbles: true });
        selectElement.dispatchEvent(event);
        '''
    driver.execute_script(js)
    time.sleep(4)
    global unmatched
    limit=0 # check how many time we got revenue less than 4 million
    data=[]
    while True:
        time.sleep(4)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.XPATH,'//a[text()="»"]')))
        results = driver.find_elements(By.XPATH, '//div[@class="listing"]')
        try:
            for result in results:
                try:
                    revenue_element = result.find_element(By.XPATH, './/span[text()="Revenue:"]/..')
                    revenue = revenue_element.text
                except Exception as e:
                    revenue=''
                    print(str(e))
                atag_element = result.find_element(By.XPATH, './/button[text()="View Details"]')
                atag =  "https://fcbb.com"+atag_element.get_attribute('data-url')
                bol= cashflow_revenue_checker(revenue)
                if bol:
                    data.append(atag)
                else:
                    unmatched+=1
            try:
                if 'paginate active'==driver.find_element(By.XPATH, '//a[text()="»"]/preceding-sibling::a[1]').get_attribute('class'):
                    break
                driver.find_element(By.XPATH, '//a[text()="»"]').click()
            except:
                try:
                    driver.find_element(By.XPATH, '//a[text()="»"]').click()
                except:
                    print("Next button not found")
        except Exception as e:
            print(str(e))
            break
    return data

if __name__ == "__main__":
    first=[]
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    allhref = main_page(base_url,driver)
    unique_urls = set(allhref)-set(last)
    if len(unique_urls)>0:
        for i in unique_urls:
            fetch_data(i)
        update_first(list(unique_urls))
    driver.quit()
    print("Scraping completed.")
