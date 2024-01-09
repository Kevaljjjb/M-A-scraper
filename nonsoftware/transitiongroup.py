from lxml import html
import  csv
import pytz
from datetime import datetime
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import  webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 

last_csv='./config/last_transitiongroup.csv'
old_href=[]
last_count=0
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader)
    old_href = []

    for row in reader:
        old_href.append(row[0])

main_file='output.csv'
base_url = "https://thetransitiongroup.biz/businesses-for-sale/"

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
                location = driver.find_element(By.XPATH, '//span[contains(text(),"Location:")]/following-sibling::span').text
                state=location
            except Exception as e:
                location = 'N/A'
                # print(f"An error occurred: {e}")

            # print(city)
            source='Transitiongroup.com'
            try:
                revenue=driver.find_element(By.XPATH, '//span[contains(text(),"Total Sales:")]/following-sibling::span').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//span[contains(text(),"Cash Flow:")]/following-sibling::span').text
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//span[contains(text(),"Inventory:")]/following-sibling::span').text
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//div[text()="Gross Income"]/following-sibling::div').text
            except:
                ebitda='N/A'
            try:
                description = driver.find_element(By.XPATH, '//div[contains(text(),"Description")]/following-sibling::p').text
            except:
                description='N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//div[@class="deal-owner"]').text
                listedby=''.join(listedby).strip()
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                phone = driver.find_element(By.XPATH, '//div[contains(text(),"Phone: ")]/a[contains(@href,"tel:")]').text
            except:
                phone='N/A'
            try:
                mail = driver.find_element(By.XPATH, '//div[contains(text(),"Email: ")]/a[contains(@href,"mailto:")]').text
            except:
                mail='N/A'

            try:
                industry=driver.find_element(By.XPATH,'//span[contains(text(),"Industry:")]/following-sibling::span').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//span[contains(text(),"Price:")]/following-sibling::span').text
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

            data_tocsv=[title,city,state,country,i,industry,source,description,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
            save_to_csv(data_tocsv)

        except Exception as e:
            import traceback
            print(f"An error occurred while fetching data from {i}: {str(e)} \n")
            traceback_message = traceback.format_exc()
            print(traceback_message)
            continue

    return []
new_count=0
def save_to_csv(data):
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            writer=csv.writer(f)
            writer.writerow(data)

def main_page(driver,url):
    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="listing-box"]//div[@class="listing-title"]/a')))

        # Get the page source after it's loaded
        page_source = driver.page_source

        # Parse the HTML content of the page
        tree = html.fromstring(page_source)

        # Extract data using XPath
        results = tree.xpath('//div[@class="listing-box"]//div[@class="listing-title"]/a')
        hrefs = []

        # Process the extracted data
        for result in results:
            href = result.xpath('.//caption//a/@href')
            hrefs.extend(href)
        

        # Check if there is a "Next" button for the next page
        next_page_url = tree.xpath('//a[contains(text(),"NEXT")]/@href')

        return hrefs, next_page_url[0] if next_page_url else None
    except:
        return [],None

def update_href(data):
    with open(last_csv,"a",newline='')as f:
        w=csv.writer(f)
        for i in data:
                w.writerow([i])
def main(driver):
    driver.get(base_url)
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="listing-box"]//div[@class="listing-title"]/a')))
    results = driver.find_elements(By.XPATH,'//div[@class="listing-box"]//div[@class="listing-title"]/a')
    urls=[]
    for i in results:
        urls.append(i.get_attribute('href'))
    return urls


if __name__ == "__main__":
    current_url = base_url
    # Set up the Selenium WebDriver (you need to download the appropriate driver and provide its path)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    first=[]    
    new_href=main(driver)
    
    unique_href = list(set(new_href) - set(old_href))
    fetch_data(driver,unique_href)
    update_href(unique_href)
    print("Scraping completed.")

    driver.quit()