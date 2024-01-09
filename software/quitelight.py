import requests
from lxml import html
import concurrent.futures
import  csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pytz 
from datetime import datetime 


last_csv='./config/last_quitelight.csv'
last=[]

with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader,None)
    last = []

    for row in reader:
        last.append(row[0])



# Define the URL
main_file='Soft_data.csv'

def fetch_data(url,industry,revenue):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    if '$'  in revenue:
            numeric_value = int(revenue.replace('$', '').replace(',', '').replace("Revenue: ",""))
            if numeric_value > 1000000:
                try:
                    # Send an HTTP GET request to the URL
                    headers = {'User-Agent': user_agent}
                    response = requests.get(url,headers=headers)

                    # Check if the request was successful (status code 200)
                    if response.status_code == 200:
                        # Parse the HTML content of the page using lxml
                        page_content = html.fromstring(response.text)

                        # Extract the data you need from the page_content (same code as before)
                        try:
                            title=page_content.xpath('(//div[@class="container"])[1]/h3/text()')[0]
                        except:
                            title=''
                        city='N/A'
                        state='N/A'
                        country='N/A'
                        source='quietlight.com'
                        try:
                            revenue=page_content.xpath("//h6[contains(text(),'REVENUE')]/following-sibling::p/text()")[0]
                        except:
                            revenue=''
                        try:
                            desc=page_content.xpath("//div[@class='inform_price single_business_price']/p//text()")
                            decription=''.join(desc)
                        except:
                            description=''
                        try:
                            listedby=page_content.xpath('//div[@class="advisor_para"]/h1/text()')[0]
                        except:
                            listedby=''
                        listedby_firm='N/A'
                        phone='N/A'
                        mail='N/A'

                        try:
                            asking=page_content.xpath('//div[@class="inform_price single_business_price"]/h4/text()')[0]
                            # print("Asking is :" ,asking)
                            ask=asking.replace("Asking Price:",'').strip()
                        except:
                            ask=''
                         # Get the current date and time in UTC
                        current_datetime = datetime.now(pytz.utc)

                        # Convert to Eastern Daylight Time (EDT)
                        eastern = pytz.timezone("US/Eastern")
                        current_datetime_edt = current_datetime.astimezone(eastern)

                        # Format the date as mm/dd/yy
                        formatted_date = current_datetime_edt.strftime("%m/%d/%Y")

                        # print([title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,gross])
                        if url  not in last :
                            data_to_send=[title,city,state,country,url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,'N/A','N/A','N/A',formatted_date]
                            save_to_csv(data_to_send)
                            update_first(url)

                    else:
                        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")

                except Exception as e:
                    print(f"An error occurred while fetching data from {url}: {str(e)}")

                return []
            else:
                print('Less than 2 mil')
        
def save_to_csv(data):
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            writer=csv.writer(f)
            writer.writerow(data)

def  update_first(data):
     with open(last_csv,'a',newline='',encoding='utf-8')as f:
            w=csv.writer(f)
            w.writerow([data])  
# Define the URL
def main_page():
    # Set up Chrome WebDriver
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    url = "https://quietlight.com/listings/"

    try:
        # Load the URL using Selenium WebDriver
        driver.get(url)

        # Wait for the page to load (you can adjust the sleep duration as needed)
        time.sleep(3)

        # Extract data from the loaded page
        listing_elements = driver.find_elements(By.XPATH, "//div[not(contains(@style, ' display: none;')) and contains(@class, 'single-content') and contains(@class, 'grid-item')]//a[@class='btn_links']/..")
        hrefs = []
        industry = []
        revenues=[]

        for element in listing_elements:
            try:
                href = element.find_element(By.XPATH, './/a[@class="btn_links"]').get_attribute("href")
            except:
                href = ''

            try:
                indus = element.find_element(By.XPATH, './/div[@class="ecom_img"]/following-sibling::p').text
                # indus = ''.join(indus).strip()
            except:
                indus = ''
            try:
                rev=element.find_element(By.XPATH,'.//p[contains(text(),"Revenue")]').text
            except:
                revenue='' 
            revenues.append(rev)
            industry.append(indus)
            hrefs.append(href)
        # print(hrefs, industry,revenues)
        for i in range(len(hrefs)):            
            fetch_data(hrefs[i], industry[i],revenues[i])

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()  # Close the WebDriver when done



if __name__ == "__main__":
    main_page()
        


# main div selection //div[not(contains(@style, ' display: none;')) and contains(@class, 'single-content') and contains(@class, 'grid-item')]
# price //div[@class='price']//text