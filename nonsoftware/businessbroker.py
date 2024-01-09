
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
import pytz
import requests
import re
import csv           
import concurrent.futures

last_csv='./config/last_businessforsale.csv'
last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    last = []
    for row in reader:
        last.append(row[0])

# Define the URL
main_file='./output.csv'
urls = []

# Function to process JSON data
def get_urls(json_data):
    for block in json_data["d"]:
        cash_flow = block["CashFlow"]
        yearly_revenue = block["YearlyRevenue"]
        url = block["URL"]
        if '$' in cash_flow:
            cash_fl= re.sub(r"[^\d\-+\.]", "", cash_flow)
            cashflow=int(cash_fl)
            if cashflow >2000000:
                urls.append(url)
        elif  "$" in yearly_revenue:
            rev= re.sub(r"[^\d\-+\.]", "", yearly_revenue)
            revenue=int(rev)
            if revenue >= 4000000:
                urls.append(url)
        else:
            print('both missing')

        
def fetch_data(url):
    url="https://www.businessbroker.net"+url
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    try:
         # Get the page
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        title = wait.until(EC.presence_of_element_located((By.XPATH, '//h1[@class="title white-text bold"]')))
        try:
            title = driver.find_element(By.XPATH, '//h1[@class="title white-text bold"]').text.strip()
        except:
            title = 'N/A'

        city = 'N/A'
        state = 'N/A'
        country = 'N/A'
        try:
            location = driver.find_element(By.XPATH, '//h2[@class="location white-text"]').text.strip()
            if ',' in location:
                city,state=location.split(',')
            else:   
                city=location
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
        # driver.quit()
        
        # code to get the date from the edt time
        # Get the current date and time in UTC
        current_datetime = datetime.now(pytz.utc)

        # Convert to Eastern Daylight Time (EDT)
        eastern = pytz.timezone("US/Eastern")
        current_datetime_edt = current_datetime.astimezone(eastern)

        # Format the date as mm/dd/yy
        formatted_date = current_datetime_edt.strftime("%m-%d-%y")

        data_tocsv=[title,city,state,country,url,industry,source,description,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
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
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            global new_count
            writer=csv.writer(f)
            writer.writerow(data)
            # print(new_count)
            new_count+=1
            if new_count==1:
                update_first(data)

def  update_first(data):
     with open(last_csv,'w',newline='',encoding='utf-8')as f:
          w=csv.writer(f)
          w.writerow(headers)
          w.writerow(data)  



# Set the URL and headers for the request
url = "https://www.businessbroker.net/webservices/dataservice.asmx/getlistingdata"
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.7",
    "Content-Type": "application/json; charset=UTF-8",
    "Cookie": "ARRAffinity=408c4d99f472f04ce10dfdca490f9ca59f86d6a8d759d6590e43248def3d6269; ARRAffinitySameSite=408c4d99f472f04ce10dfdca490f9ca59f86d6a8d759d6590e43248def3d6269; VisitorId=22e11524-1eaa-4784-be67-faf1b5265fbd; VisitorSessionId=d2defe18-9fd9-4169-920b-734f71bbb561; VisitorState=UT; VisitorMap_Id=52; VisitorContinent=6; CartWinbackEmail=0; ASP.NET_SessionId=n3teqfshz0rogwosqexgwmdo; wp42850=\"XVBYTDDDDDDUKVAJLUV-BLXM-XIZW-BCZT-AXXLMLCAAKKUDCMTBYWTY-ZJAL-XMMX-CVVH-WHBZMLLKKVJADINlpgLllIkhrLk_gLmDD\"",
    "Origin": "https://www.businessbroker.net",
    "Referer": "https://www.businessbroker.net/listings/bfs_result.aspx?by=advancedsearch&r_id=33&ind_id=0&ask_price_l=4000000&ask_price_h=0&map_id=0&lcity=&keyword=&lst_no=&time=0&bprice=0&fresale=0&ownerfi=0&county_id=0&page=27",
    "Sec-Ch-Ua": "\"Chromium\";v=\"118\", \"Brave\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Gpc": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

# Initial startAt value
start_at = 2

# Loop through multiple requests, changing the startAt value each time
while True:
    payload ={'strIndId':'0', 'strIndAlias':'', 'regId':33, 'regParentId':0, 'askPriceLow':4000000, 'askPriceHigh':0, 'mapId':0, 'strCity':'', 'strKeyword':'', 'timeFrame':0, 'noPrice':0, 'franchiseResale':0, 'ownerFinancing':0, 'countyId':0, 'strListedOnDate':'', 'sortBy':'l.flisting DESC, l.ldate DESC', 'startAt':start_at, 'howMany':30, 'includeFranchise':'false', 'franchiseListingFrequency':4, 'initialHowMany':30, 'featuredListing':0}

    response = requests.post(url, headers=headers, json=payload)
    if start_at == 902:
        break
    if response.status_code == 200:
        try:
            data = response.json()
            get_urls(data)
            # Increment startAt for the next request
            start_at += 30
        except ValueError:
            print("Response is not valid JSON.")
            break
    else:
        print(f"Request failed with status code {response.status_code}")
        break


num_workers =10

with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    # Use the map function to apply the fetch_data function to each URL in parallel
    results = list(executor.map(fetch_data, urls))
