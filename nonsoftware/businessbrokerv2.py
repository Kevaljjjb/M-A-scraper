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

mainfile="output.csv"
last_csv='./config/last_businessbroker.csv'
last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    last = []

    for row in reader:
        last.append(row[0])


def fetch_data(driver,urls):
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
                location = driver.find_element(By.XPATH, '//h2/span[1]').text.strip()
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    city=location
                country=driver.find_element(By.XPATH, '//h2/span[2]').text
            except Exception as e:
                location = 'N/A'
                print(f"An error occurred: {e}")

            # print(city)
            source='businessbroker.com'
            try:
                revenue=driver.find_element(By.XPATH, '//span[@id="lblyrevenue2"]').text.strip()
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//span[@id="lblycflow"]').text.strip()
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
                desc = driver.find_elements(By.XPATH, '//div[@class="columns medium-6 large-7 busListingContent"]/p[2] | //div[@class="columns medium-6 large-7 busListingContent"]/p[3]')
                description = ''.join([element.text for element in desc ]).strip()
            except:
                description = 'N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//span[@id="lblSeller"]').text
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
                industry=driver.find_element(By.XPATH,'//p[@class="industry"]').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[@id="lblPrice2"]').text
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
    with open(mainfile,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            global new_count
            writer=csv.writer(f)
            writer.writerow(data)

def  update_first(data):
     with open(last_csv,'a',newline='')as f:
          w=csv.writer(f)
          for i in data:
            w.writerow([i])     

def cashflow_revenue_checker(cash,rev):
    if '$' in cash:
        # print(cash)
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        try:
            value = float(value)
        except:
            return False
        if value >= 2000000:
            return True
        else:
            return False  # You were missing the return statement here
    elif '$'in rev:
        # print(cash)
        value = re.sub(r"[^\d\-+\.]", "", rev)
        # Convert the value to a float.
        try:
            value = float(value)
        except:
            return False
        if value >= 4000000:
            return True
        else:
            return False

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
    for i in range(1,5):
        base_url=f'https://www.businessbroker.net/listings/bfs_result.aspx?By=AdvancedSearch&r_id=33&ind_id=0&ask_price_l=3000000&ask_price_h=&map_id=12&lcity=&keyword=&lst_no=&time=0&bprice=0&fresale=0&ownerfi=0&county_id=0&sort_list=cash_flow_DESC&page={str(i)}'
        driver.get(base_url)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//a[text()="Read More"]')))
            results=driver.find_elements(By.XPATH,'//div[@class="result-item listing"]')
            for i in results:
                cf=i.find_element(By.XPATH,'.//span[text()="Cash Flow"]/..').text.replace("Cash Flow","")
                rev=i.find_element(By.XPATH,'.//span[text()="Revenue"]/..').text.replace("Revenue","")
                if cashflow_revenue_checker(cf,rev):
                    href=i.find_element(By.XPATH,".//a[text()='Read More']").get_attribute('href')
                    urls.append(href)
        except Exception as e:
            print(str(e))
            break
    return urls

if __name__ == "__main__":
    allhref=main()
    unique_urls = set(allhref)-set(last) 
    if len(unique_urls)>0:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={user_agent}')
        # options.add_argument(f'--headless')
        driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
        fetch_data(driver,unique_urls)
        update_first(unique_urls)