import requests
from lxml import html
import  csv
import concurrent.futures
import pytz
from datetime import datetime
from selenium import  webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


# Define the URL
headers = ['Title', 'City', 'State', 'Country', 'URL', 'Industry', 'Source', 'Description',
           'Listed By (Firm)', 'Listed By (Name)', 'Phone', 'Email', 'Price', 'Gross Revenue',
           'Cash Flow', 'Inventory', 'EBITDA','Scraping Date','listing Date','Financial Data']

last_csv='./config/last_businessforsale.csv'
old_href=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader)

    for row in reader:
        old_href.append(row[0])

main_file='output.csv'
with open(main_file, 'w',newline='') as file:
    writer=csv.writer(file)
    writer.writerow(headers)
base_url = "https://us.businessesforsale.com/us/search/businesses-for-sale?Profit.From=2000000&ProfitDisclosedOnly=1"
def fetch_data(url):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        try:
            # Send an HTTP GET request to the URL
            headers = {'User-Agent': user_agent}
            response = requests.get(url,headers=headers) 

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the HTML content of the page using lxml
                page_content = html.fromstring(response.text)
                title=page_content.xpath('//div[@id="title-address"]//h1/text()')[0]
                # Extract the data you need from the page_content (same code as before)
                try:
                    title=page_content.xpath('//div[@id="title-address"]//h1/text()')[0]
                    title=''.join(title).strip()
                except:
                    title='N/A'

                city='N/A'
                state='N/A'
                country='N/A'
                try:
                    location=page_content.xpath('//div[@id="address"]//span/text()')
                    if len(location)>2:
                        city=location[0]
                        state=location[1]
                        country=location[2]
                    else:
                        state=location[0]
                        country=location[1]
                except:
                    location='N/A'

                
                source='businessesforsale.com'
                try:
                    revenue=page_content.xpath("//dt[contains(text(),'Sales Revenue:')]//following-sibling::dd/strong/text()")[0]
                except:
                    revenue='N/A'
                try:
                    cashflow=page_content.xpath("//dt[contains(text(),'Cash Flow: ')]//following-sibling::dd/strong/text()")[0]
                except:
                    cashflow='N/A'
                try:
                    inventory=page_content.xpath("//dt[contains(text(),'Inventory / Stock value:')]/following-sibling::dd/text()")[0]
                    inventory=''.join(inventory).strip()
                except:
                    inventory='N/A'
                try:
                    ebitda=page_content.xpath("//b[contains(text(),'EBITDA:')]/following-sibling::b[1]/text()")[0]
                except:
                    ebitda='N/A'
                
                try:
                    desc=page_content.xpath("//div[@class='listing-section-content']//text()")
                    decription=''.join(desc).strip()
                except:
                    decription='N/A'
                try:
                    listedby=page_content.xpath('//a[@rel="broker-dir"]/text()')[0]
                    listedby=''.join(listedby).strip()
                except:
                    listedby='N/A'
                try:
                    gross=page_content.xpath('//h6[contains(text(),"INCOME")]/following-sibling::p/text()')[0]
                except:
                    gross='N/A'
                try:
                    listedby_firm=page_content.xpath('//div[@class="broker-details"]//h4/text()')[0]
                    listedby_firm=''.join(listedby_firm).strip()
                except:
                    listedby_firm='N/A'
                try:
                    phone=page_content.xpath('(//a[@id="phone"]/text())[2]')[0]
                    print(phone)
                except:
                    phone='N/A'
                mail='N/A'
                try:
                    industry=page_content.xpath('(//a[@id="phone"]/text())[2]')[0]
                except:
                    industry='N/A'
                try:
                    asking=page_content.xpath('//dt[contains(text(),"Asking Price")]/following-sibling::dd//text()')
                    ask=''.join(asking).strip()
                except:
                    ask='N/A'

                current_datetime = datetime.now(pytz.utc)

                # Convert to Eastern Daylight Time (EDT)
                eastern = pytz.timezone("US/Eastern")
                current_datetime_edt = current_datetime.astimezone(eastern)

                # Format the date as mm/dd/yy
                formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

                # print([title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,gross])
                return [title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]

            else:
                print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")

        except Exception as e:

            try:
                # Send an HTTP GET request to the URL
                headers = {'User-Agent': user_agent}
                response = requests.get(url,headers=headers)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Parse the HTML content of the page using lxml
                    page_content = html.fromstring(response.text)
                    title=page_content.xpath('//div[@class="hero-copy"]//h1/text()')[0]
                    # Extract the data you need from the page_content (same code as before)
                    try:
                        title=page_content.xpath('//div[@class="hero-copy"]//h1/text()')[0]
                        title=''.join(title).strip()
                    except:
                        title='N/A'

                    city='N/A'
                    state='N/A'
                    country='N/A'
                    try:
                        location=page_content.xpath('//div[@class="teaser-field-copy"]//h3[contains(text(),"Location")]/../text()')
                        if len(location)>2:
                            city=location[0]
                            state=location[1]
                            country=location[2]
                        else:
                            state=location[0]
                            country=location[1]
                    except:
                        location='N/A'

                    
                    source='businessesforsale.com'
                    try:
                        revenue=page_content.xpath("//dt[contains(text(),'Revenue:')]//following-sibling::dd//text()")[0]
                    except:
                        revenue='N/A'
                    try:
                        cashflow=page_content.xpath("//dt[contains(text(),'Cash Flow: ')]//following-sibling::dd/strong/text()")[0]
                    except:
                        cashflow='N/A'
                    try:
                        inventory=page_content.xpath("//dt[contains(text(),'Inventory / Stock value:')]/following-sibling::dd/text()")[0]
                        inventory=''.join(inventory).strip()
                    except:
                        inventory='N/A'
                    try:
                        ebitda=page_content.xpath("//b[contains(text(),'EBITDA:')]/following-sibling::b[1]/text()")[0]
                    except:
                        ebitda='N/A'
                    
                    try:
                        desc=page_content.xpath("//div[@class='teaser-field-copy']//h3[contains(text(),'Business Description')]/..//text()")
                        decription=''.join(desc).strip()
                        a="Business Description\n"
                        decription=decription.replace(a,'')
                        # fin_desc=page_content.xpath("//div[@class='teaser-field-copy']//h3[contains(text(),'Business Description')]/..//text()")
                        # decription2=' '.join(fin_desc).strip()
                        # decription=decription2+decription2
                    except:
                        decription='N/A'
                    try:
                        listedby=page_content.xpath('//a[@rel="broker-dir"]/text()')[0]
                        listedby=''.join(listedby).strip()
                    except:
                        listedby='N/A'
                    try:
                        gross=page_content.xpath('//h6[contains(text(),"INCOME")]/following-sibling::p/text()')[0]
                    except:
                        gross='N/A'
                    try:
                        listedby_firm=page_content.xpath('//div[@class="contactBrokerInfo"]/p[2]/text()')[0]
                        listedby_firm=' '.join(listedby_firm).strip()
                    except:
                        listedby_firm='N/A'
                    try:
                        phone=page_content.xpath('(//a[@id="phone"]/text())[2]')[0]
                        print(phone)
                    except:
                        phone='N/A'
                    mail='N/A'
                    try:
                        industry=page_content.xpath('(//a[@id="phone"]/text())[2]')[0]
                    except:
                        industry='N/A'
                    try:
                        asking=page_content.xpath('//dt[contains,"Asking Price")]/following-sibling::dd//text()')
                        ask=''.join(asking).strip()
                    except:
                        ask='None'

                    try:
                        financial_data=page_content.xpath("//div[@class='teaser-field-copy']//h3[contains(text(),'Financial Summary')]/..//text()")
                        # print(financial_data)
                        a='''
Financial Summary
'''
                        fin_desc=''
                        for i in financial_data:
                            fin_desc+=i
                        fin_desc=fin_desc.replace(a,'')
                        # fin_desc=''.join(financial_data)
                    except Exception as e:
                        print(e)
                        fin_desc='N/A'

                    current_datetime = datetime.now(pytz.utc)

                    # Convert to Eastern Daylight Time (EDT)
                    eastern = pytz.timezone("US/Eastern")
                    current_datetime_edt = current_datetime.astimezone(eastern)

                    # Format the date as mm/dd/yy
                    formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

                    # print([title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,gross])
                    return [title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date,"N/A",fin_desc]

                else:
                    print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
            except:
                print(f"An error occurred while fetching data from {url}: {str(e)}")
                return None

        return []
                
def save_to_csv(data):
       with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            writer=csv.writer(f)
            writer.writerows(data)

    
def inside_page(urls):
        data = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Submit tasks for each URL and collect the results
            results = executor.map(fetch_data, urls)

        for result in results:
            if result:
                data.append(result)

        save_to_csv(data)

def main_page(driver,url):
    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="result"]')))

        # Get the page source after it's loaded
        page_source = driver.page_source

        # Parse the HTML content of the page
        tree = html.fromstring(page_source)

        # Extract data using XPath
        results = tree.xpath('//div[@class="result"]')
        results2 = tree.xpath('//div[@class="mv-result"]')
        hrefs = []

        # Process the extracted data
        for result in results:
            href = result.xpath('.//caption//a/@href')
            hrefs.extend(href)
        for a in results2:
            href = a.xpath('.//h2/a/@href')
            hrefs.extend(href)

        # Check if there is a "Next" button for the next page
        next_page_url = tree.xpath('//a[contains(text(),"NEXT")]/@href')

        return hrefs, next_page_url[0] if next_page_url else None
    except:
        return [],None

def update_href(data):
    with open(last_csv,"a",newline='')as f:
        w=csv.writer(f)
        # w.writerow(["Urls"])
        for i in data:
                w.writerow([i])


if __name__ == "__main__":
    current_url = base_url
    # Set up the Selenium WebDriver (you need to download the appropriate driver and provide its path)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    first=[]    
    new_href=[]
    while current_url:
        hrefs, next_page_url = main_page(driver,current_url)

        # Fetch data from the current page
        new_href.extend(hrefs)

        # Update the current URL to the next page URL
        if next_page_url==None:
             break
        current_url = next_page_url
    unique_href = list(set(new_href) - set(old_href))
    allhref=list(set(new_href+old_href))
    if len(unique_href)>0:
        inside_page(unique_href)
        update_href(unique_href)

    print("Scraping completed.")

    driver.quit()