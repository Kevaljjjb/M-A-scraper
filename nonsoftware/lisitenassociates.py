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

# Define the header values
headers = ['Title', 'City', 'State', 'Country', 'URL', 'Industry', 'Source', 'Description',
           'Listed By (Firm)', 'Listed By (Name)', 'Phone', 'Email', 'Price', 'Gross Revenue',
           'Cash Flow', 'Inventory', 'EBITDA','scraped Date']
last_csv='./config/last_lisitenassociates.csv'
last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)

    for row in reader:
        last.append(row[0])


# Define the URL
main_file='output.csv'
base_url = "https://lisitenassociates.com/exclusive-listings/"

def cashflow_revenue_checker(cash):
    if '$' in cash:
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        try:
            value = int(value)
        except:
            return False
        if value >= 2000000:
            return True
        else:
            return False  # You were missing the return statement here
    else:
        return False

def fetch_data(driver,urls):
    for i in urls:
        try:
            driver.get(i)
            wait = WebDriverWait(driver, 20)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="main-title"]')))
            tree = html.fromstring(driver.page_source)
            try:
                title = driver.find_element(By.XPATH, '//span[@class="main-title"]').text
            except:
                title = 'N/A'

            city = 'N/A'
            state = 'N/A'
            country = 'N/A'
            try:
                location = driver.find_element(By.XPATH, '//span[@class="cityheading"]').text
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    state=location
            except Exception as e:
                location = 'N/A'
                # print(f"An error occurred: {e}")

            print(city)
            source='lisitenassociates.com'
            try:
                # gross_revenue = main_details_section.find_element(By.XPATH, '//span[contains(@class, "label") and contains(text(), "Gross Revenue")]')
                revenue = tree.xpath('//span[contains(text(), "Gross Revenue: ")]/following-sibling::text()')[0]

                # revenue=driver.find_element(By.XPATH, '//span[text()="Gross Revenue:"]/following-sibling::*').text
            except Exception as e:
                print(str(e))
                revenue='N/A'
            try:
                cashflow=tree.xpath('//span[text()="Cash Flow: "]/following-sibling::text()')[0]
            except:
                cashflow='N/A'

            try:
                inventory=tree.xpath('//span[text()="Inventory: "]/following-sibling::text()')[0]
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//span[text()="EBITDA:"]/following-sibling::*').text
            except:
                ebitda='N/A'
            try:
                desc=driver.find_element(By.XPATH,'//span[text()="Business Description: "]/following-sibling::*')
                # Concatenate the text content
                description = ''.join(desc.text ).strip()
            except:
                description='N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//div[@class="broker"]/h3').text.replace("Business Listed By:","").replace("\n","")
                listedby=''.join(listedby).strip()
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                phone=driver.find_element(By.XPATH,'//img[@alt="tal"]/following-sibling::span').text
                mail=driver.find_element(By.XPATH,'//span[@id="hd_con_email"]/a').text
                        
            except:
                phone='N/A'
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//h6[contains(text(),"Listed Price:")]/strong').text
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

            data_tocsv=[title,city,state,country,driver.current_url,industry,source,description,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
            save_to_csv(data_tocsv)

        except Exception as e:
            import traceback
            print(f"An error occurred while fetching data from {i}: {str(e)} \n")
            traceback_message = traceback.format_exc()
            print(traceback_message)
            continue

    return []
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

get_cashflow = lambda cf: cf.split("\n")[0].replace("Cash Flow: ", "")

def main(driver):
    driver.get(base_url)
    wait = WebDriverWait(driver, 20)
    urls = []

    while True:
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(),"Cash Flow")]/..')))
            results = driver.find_elements(By.XPATH, '//div[@class="listing featured page1"]')

            for i in results:
                try:
                    cf = i.find_element(By.XPATH, './/span[contains(text(),"Cash Flow")]/..').text
                    cash=get_cashflow(cf)
                except:
                    cash="$0"
                bol = cashflow_revenue_checker(cash)
                link = i.find_element(By.XPATH, './/a[text()="View Listing"]').get_attribute("href")

                if bol:
                    urls.append(link)
                else:
                    continue
            try:
                next_button = driver.find_element(By.XPATH, '//a[@rel="next"]')
                next_button.click()
                driver.switch_to.default_content()
                wait.until(EC.staleness_of(next_button))  # Wait for the next button to be stale
            except :
                print("No more pages")
                break
        except Exception   as te:
            print(f"{str(te)}")
            break
     # Make sure to close the driver
    return urls


if __name__ =="__main__":
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    links=main(driver)
    unique=set(links)-set(last)
    fetch_data(driver,unique)
    update_first(unique)
    driver.close()