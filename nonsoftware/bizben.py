import requests
from lxml import html
import  csv
import concurrent.futures
import time
import re
import pytz
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set the local driver path
driver_path = "./config/chromedriver.exe"

# Create a new ChromeOptions instance
chrome_options = webdriver.ChromeOptions()

# Specify the local driver path
chrome_options.add_argument("--executable-path={}".format(driver_path))

# Create a new WebDriver instance using the ChromeOptions instance
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=chrome_options)
driver.get('https://www.bizben.com/business-for-sale/bizben-search-advanced.php')
time.sleep(3)
scroll_distance = 500
scroll_script = f"window.scrollBy(0,{scroll_distance});"
filter_js='''btn=document.querySelector("#inlineCheckbox12");
             btn.checked=true;
            '''
driver.execute_script(filter_js)
time.sleep(5)
driver.execute_script(scroll_script)

try:
    driver.find_element(By.XPATH,'//input[@value="Show All Search Results"]').click()
except:
    driver.find_element(By.XPATH,'//input[@value="Show All Search Results"]').click()

base_url=driver.current_url

driver.quit()

last_csv='./config/last_bizben.csv'
last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)

    for row in reader:
        last.append(row[0])
main_file='./output.csv'

def fetch_data(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

    # print("Here is is the  URL :"+url)
    try:
        # Send an HTTP GET request to the URL
        headers = {'User-Agent': user_agent}
        response = requests.get(url,headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using lxml
            page_content = html.fromstring(response.text)
            title=page_content.xpath('//h1[contains(@class,"semiBold text font24")]/span[1]/text()')[0]
            # Extract the data you need from the page_content (same code as before)
            try:
                title=page_content.xpath('//h1[contains(@class,"semiBold text font24")]/span[1]/text()')[0]
                title=''.join(title.strip())
                title=title.replace('For Sale:','')
                
            except:
                title='N/A'

            city = 'N/A'
            state = 'N/A'
            country = 'N/A'
            # try:
            #     state = page_content.xpath('//p[contains(text(),"Address:")]/span/text()')[0]

            # except Exception as e:
            #     state = 'N/A'


            try:
                    city=page_content.xpath('//p[contains(text(),"City:")]//span[@class="text-muted txtnormal ms-2"]/text()')[0]
            except:
                    city=''
            try:
                    state=page_content.xpath('//p[contains(text(),"Area:")]//span[@class="text-muted txtnormal ms-2"]/text()')[0]
            except:
                    state=''

            source='Bizben.com'
            try:
                revenue=page_content.xpath('//p[contains(text(),"Revenue")]//span[@class="text-muted txtnormal ms-2"]/text()')[0]
                revenue=''.join(revenue).strip()
            except:
                revenue='N/A'
            try:
                cashflow=page_content.xpath('//p[contains(text(),"Cash Flow:")]//span[@class="text-muted txtnormal ms-2"]/text()')[0]
                cashflow=''.join(cashflow).strip()
            except:
                cashflow='N/A'
            try:
                inventory=page_content.xpath('//di),"Inventory")]/following-sibling::div/text()')[0]
            except:
                inventory='N/A'
            try:
                ebitda=page_content.xpath("//b[contains(text(),'EBITDA:')]/following-sibling::b[1]/text()")[0]
            except:
                ebitda='N/A'
            
            try:
                desc = page_content.xpath('//div[@itemprop="description"]//text()')
                desc_text = ''.join(desc).strip()
                description = desc_text if desc_text else 'N/A'
            except Exception as e:
                print(e)
                description = 'N/A'

            try:
                listedby=page_content.xpath('//li[contains(text(),"Name:")]//span[@class="text-muted txtnormal ms-2"]/text()')[0]
                listedby=''.join(listedby).strip()
            except:
                listedby='N/A'
            try:
                listedby_firm=page_content.xpath('//h3[@class="media-heading"]//a/text()')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                phone=page_content.xpath('//li[contains(text(),"Phone:")]//span[@class="text-muted txtnormal ms-2"]/text()')[0]
            except:
                phone='N/A'
            mail='N/A'
            try:
                industry=page_content.xpath('//li[@cladcrumb-item active text"]/text()')[0]
            except:
                industry='N/A'
            try:
                ask=page_content.xpath('//p[contains(text(),"Asking Price:")]//span[@class="text-muted txtnormal ms-2"]/text()')[0]
                ask=''.join(ask).strip()
            except:
                ask='N/A'

            try:
                listed_date=driver.find_element(By.XPATH,'(//i[@class="fa fa-clock-o"])[1]/following-sibling::span').text
            except:
                listed_date=''

            current_datetime = datetime.now(pytz.utc)

            # Convert to Eastern Daylight Time (EDT)
            eastern = pytz.timezone("US/Eastern")
            current_datetime_edt = current_datetime.astimezone(eastern)

            # Format the date as mm/dd/yy
            formatted_date = current_datetime_edt.strftime("%m/%d/%Y")



            # print([title,city,state,country,url,industry,source,description,listedby_firm,listedby,phone,mail,ask,revenue,gross])
            return [title,city,state,country,url,industry,source,description,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date,listed_date]

        else:
            print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred while fetching data from {url}: {str(e)}")
    return []

def save_to_csv(data):    
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            global new_count
            global  first
            writer=csv.writer(f)
            writer.writerows(data)
            

def  update_first(data):
     with open(last_csv,'a',newline='')as f:
          w=csv.writer(f)
          for i in data:
            w.writerow([i])            

def inside_page(urls):
        data = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Submit tasks for each URL and collect the results
            results = executor.map(fetch_data, urls)

        for result in results:
            if result:
                data.append(result)

        save_to_csv(data)

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
def main_page(url):
    # Send a GET request to the URL
    try:
        response = requests.get(url)
    except:
        time.sleep(10)
        response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        tree = html.fromstring(response.text)

        # Extract data using XPath
        results = tree.xpath('//div[@class="col col-grit for-sales-grid"]')
        hrefs = []
        # Process the extracted data
        try:
            for result in results:
                cashflow=result.xpath(".//p[contains(text(),'Cash flow')]/following-sibling::p/text()")[0]
                revenue=result.xpath(".//p[contains(text(),'Revenue')]/following-sibling::p/text()")[0]
                # print(cashflow)
                if cashflow_revenue_checker(cashflow,""):
                        atag=result.xpath('.//a[@class="text-black rlinks2"]/@href')[0]
                        atag= 'https://www.bizben.com'+atag
                        title=result.xpath('.//h5/text()')                                 
                        hrefs.append(atag)
                elif cashflow_revenue_checker("",revenue):
                    
                        atag=result.xpath('.//a[@class="text-black rlinks2"]/@href')[0]
                        atag= 'https://www.bizben.com'+atag
                        hrefs.append(atag)
                else:
                    print("<---------------------->")
        except Exception as e  :
            import traceback
            print("An error occurred:", e)
            traceback.print_exc()
            next_page_url=None
        else:
            next_page_url = tree.xpath('//li[@class="list-inline-item mx-2"]/a[contains(text(),"Next")]/@href')
            print(next_page_url)
        return hrefs, 'https://www.bizben.com/'+next_page_url[0] if next_page_url else None
    else:
        print("Failed to retrieve the web page. Status code:", response.status_code)
        return [], None

if __name__ == "__main__":
    current_url = base_url
    first=[]    
    allhref=[]
    while current_url:
        hrefs, next_page_url = main_page(current_url)
        for i in hrefs:
            allhref.append(i)
        if next_page_url == None:
            break
        elif current_url == next_page_url:
            break
        current_url = next_page_url
    unique_urls = set(allhref)-set(last) 
    if len(unique_urls) >0:
        inside_page(unique_urls)
        update_first(list(unique_urls))
    print("Scraping completed.")