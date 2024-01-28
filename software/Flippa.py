from selenium import webdriver
import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from lxml import html
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import re
import csv
from datetime import datetime
import pytz

# Set your desired user agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

url = 'https://flippa.com/search?query%5Bkeyword%5D=&search_template=most_relevant&sort_alias=&page%5Bsize%5D=75&filter%5Bprofit_per_month%5D%5Bmin%5D=41667&filter%5Bsale_method%5D=auction,classified&filter%5Bstatus%5D=open&filter%5Bproperty_type%5D=website,fba,saas,ios_app,android_app,other&filter%5Bsitetype%5D=all,content,blog,directory,review,forum-community,ecommerce,dropship,digital%20products,shopify,inventory-holding,saas,services,digital,physical,transact-market&filter%5Brevenue_generating%5D=T,F'

new_count=0
last_csv='./config/last_Flippa.csv'
last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)

    for row in reader:
        last.append(row[0])

# Define the URL
main_file='Soft_data.csv'
# Configure the webdriver with the user-agent using undetected-chromedriver
options = uc.ChromeOptions()
options.add_argument(f"user-agent={user_agent}")
options.headless = False

def login(driver):
    driver.get("https://flippa.com/login")
    time.sleep(3)
    mail=driver.find_element(By.XPATH,'//input[@type="email"]')
    mail.send_keys("shawn@teddyholdings.com")
    time.sleep(3)
    password=driver.find_element(By.XPATH,'//input[@type="password"]')
    password.send_keys("Teddy123!" +Keys.RETURN)

def inner_page(urls):
        options2 = webdriver.ChromeOptions()
        options2.add_argument(f"user-agent={user_agent}")
        options2.headless = False
        driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options2)
        for i in urls:
            url= i
            driver.get(url)
            time.sleep(2)
            try:
                wait = WebDriverWait(driver, 20)
                title = wait.until(EC.presence_of_element_located((By.XPATH, '//h2/../../following-sibling::div[1]')))
                try:
                    title = driver.find_element(By.XPATH, '//h2/../../following-sibling::div[1]').text.strip()
                except:
                    title = 'N/A'

                city = 'N/A'
                state = 'N/A'
                country = 'N/A'
                try:
                    location =driver.find_element(By.XPATH, '//p[@class="font-weight-bold letter-spacing-large text-uppercase"]').text.strip()
                    if ',' in location:
                        city,state=location.split(',')
                    else:   
                        country=location
                except Exception as e:
                    location = 'N/A'
                    print(f"An error occurred: {e}")

                source='flippa.com'
                try:
                    element=driver.find_element(By.XPATH,'//span[contains(text(),"Monthly Profit")]/following-sibling::div').text
                    value = re.sub(r"[^\d\-+\.]", "", element)
                    base = int(value)
                    print("Base :" , base)
                    print(type(base))
                    cashflow=base*12     
                    rev=driver.find_element(By.XPATH, '//span[contains(text(),"Revenue Multiple")]/following-sibling::div').text.strip()
                    val_rev=re.sub(r"[^\d\-+\.]", "", rev)
                    val_rev=float(val_rev)
                    revenue=cashflow*val_rev

                except Exception as e:
                    import traceback
                    print(f"An error occurred while fetching data from {url}: {str(e)} \n")
                    traceback_message = traceback.format_exc()
                    print(traceback_message)
                    continue
                    revenue='N/A'
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
                    desc=driver.find_element(By.XPATH,'//div[@class="listing-description"]').text
                    decription=''.join(desc).strip()
                except:
                    decription='N/A'
                try:
                    listedby=driver.find_element(By.XPATH,'//div[@class="agent-name"]').text
                    listedby=''.join(listedby).strip()
                except:
                    listedby='N/A'
                try:
                    listedby_firm=driver.find_element(By.XPATH,'//h3[@classxccac="media-heading"]//a/text()')[0]
                    listedby_firm=''.join(listedby_firm).strip()
                except:
                    listedby_firm='N/A'
                try:
                    num=driver.find_element(By.XPATH,'//div[@class="agent-phone"]').text
                    phone=''.join(num).strip() 
                except:
                    phone='N/A'
                try:
                    mail=driver.find_element(By.XPATH,'//div[@class="agent-phone"]').text
                except :
                    mail='N/A'
                try:
                    industry=driver.find_element(By.XPATH,'//div//span[text()="Category:"]/../../following-sibling::div[1]').text
                except:
                    industry='N/A'
                try:
                    ask=driver.find_element(By.XPATH,'(//span[contains(text(),"Asking Price ")])[2]/../../following-sibling::div[1]').text
                except:
                    ask='N/A'
                # driver.quit()
                
                # code to get the date from the edt time
                # Get the current date and time in UTC
                current_datetime = datetime.now(pytz.utc)

                # Convert to Eastern Daylight Time (EDT)
                eastern = pytz.timezone("US/Eastern")
                current_datetime_edt = current_datetime.astimezone(eastern)

                # Format the date as mm/dd/yy
                formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

                # check for cash flow 
                
                data_tocsv=[title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
                save_to_csv(data_tocsv)
            except Exception as e:
                import traceback
                print(f"An error occurred while fetching data from {url}: {str(e)} \n")
                traceback_message = traceback.format_exc()
                print(traceback_message)


                
def save_to_csv(data):
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            global new_count
            writer=csv.writer(f)
            writer.writerow(data)

def  update_first(data):
     with open(last_csv,'a',newline='',encoding='utf-8')as f:
          w=csv.writer(f)
          for i in data:
            w.writerow([i])  

driver = webdriver.Chrome()
hrefs=[]
try:
    login(driver)
    time.sleep(2)
    driver.get(url)
    time.sleep(1)
    response_content = driver.page_source
    driver.quit()

    tree = html.fromstring(response_content)
    urls = tree.xpath('//a[@class="card-title btn-link-unstyled stretched-link text-truncate GTM-search-result-card"]/@href')
    for i in urls:
        hrefs.append("https://flippa.com"+i)
    unique=set(hrefs)-set(last)
    inner_page(unique)
    update_first(unique)
except Exception as e:
    import traceback
    print(f"An error occurred while fetching data from {url}: {str(e)} \n")
    traceback_message = traceback.format_exc()
    print(traceback_message)