from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import pytz
from datetime import datetime
headers = ['Title', 'City', 'State', 'Country', 'URL', 'Industry', 'Source', 'Description',
           'Listed By (Firm)', 'Listed By (Name)', 'Phone', 'Email', 'Price', 'Gross Revenue',
           'Cash Flow', 'Inventory', 'EBITDA', 'Scraping Date','Financial Data','source Link']

csvfile='soft_data.csv'
with open(csvfile,'w' ,newline='') as f:
    writer=csv.writer(f)
    writer.writerow(headers)


#logic to get last url
last_csv='./config/last_kumosaas.csv'
url_value = None
# Open the CSV file for reading
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    
    # Read the header row to determine the index of the 'URL' column
    header = next(reader)  # Read the first row (header)
    url_column_index = None

    # Find the index of the 'URL' column
    for idx, column in enumerate(header):
        if column.strip().lower() == 'url':
            url_column_index = idx
            break

    # If the 'URL' column is found, extract the value
    if url_column_index is not None:
        # Assuming you want to extract the value from the first row (or any specific row)
        row = next(reader, None)  # Change this if you want to extract from a different row
        if row is not None:
            url_value = row[url_column_index]

    


# Set your desired user agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

# Set the URL
url = "https://app.withkumo.com/signin"

# Set your login credentials
username = "kyle@tuckersfarm.com"
password = "Colmar7548"

# Configure the webdriver with the user-agent
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-agent={user_agent}")

# Set up the webdriver with the Chrome driver executable path
chrome_service = ChromeService(executable_path='./config/chromedriver.exe')
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Navigate to the URL
driver.get(url)

time.sleep(4)

# Find the username and password input fields by their name attributes
username_field = driver.find_element(By.NAME, "email")
password_field = driver.find_element(By.NAME, "password")

# Enter the username and password
username_field.send_keys(username)
password_field.send_keys(password)

# Simulate pressing the Enter key to submit the form
password_field.send_keys(Keys.ENTER)

# Optional: You can perform additional actions here if needed.
time.sleep(5)

# Navigate to the initial search page
driver.get('https://app.withkumo.com/search/ngQ6FV')
time.sleep(5)
data=[]
# Define a while loop to click the "Next Page" button until it's disabled
match=False
while True:
    try:

        hrefs=driver.find_elements(By.XPATH,'//tr[@role="row"]//td[@role="gridcell"][2]//a')
        for i in hrefs:
            href=i.get_attribute('href')
            if href is not None:
                if url_value is not None: # make sure if url_value is not None
                    if url_value == href: # match the previous url with current url if found then match is true that will break the loop 
                        print('match found')
                        match=True
                        break
                data.append(href)
        if match:
            break
        # Wait for the "Next Page" button to become clickable
        next_page_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="next page"]')))
        
        # Check if the "Next Page" button is disabled
        if "disabled" in next_page_button.get_attribute("class"):
            # If the button is disabled, break the loop
            break
        
        # Click the "Next Page" button
        next_page_button.click()
        
        # Wait briefly (you can adjust the sleep time)
        time.sleep(5)
    except Exception:
        # If there's an exception, break the loop
        break

def save_last(val):
    with  open(last_csv,'w',newline='')as f:
        writer=csv.writer(f)
        writer.writerow(headers)
        writer.writerow(val)



newval_count=0 # track count of new values inserted
for url in data:

    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//p[@class="chakra-text css-4tb30n"]')))
    except:
        continue

    try:
        title=driver.find_element(By.XPATH,'//p[@class="chakra-text css-4tb30n"]').text
    except:
        title=''
    
    try:
        location=driver.find_element(By.XPATH,'(//p[@class="chakra-text css-0"])[1]').text
        location=location.replace("Location: ",'')
        match=location.split(',')
        if len(match)<=2:
            city=match[0]
            state=''
            country=match[1]
        elif len(match)>2:
            city=match[0]
            state=match[1]
            country=match[2]
        else:
            city=''
            state=''
            country=''
        print(len(match))
        # city,state,country=location.split(',')
    except:
        city=''
        state=''
        country=''

    try:
        all=driver.find_elements(By.XPATH,'//p[@class="chakra-text css-1vy54ze"]')
        industry=''
        for i in all:
            industry+=i.text+','
    except:
        industry=''

    try:
        desc=driver.find_element(By.XPATH,'//h2[text()="Description"]/following-sibling::div[1]//div').text
    except:
        desc=''
    
    try:
        ask=driver.find_element(By.XPATH,'//p[text()="Asking Price"]/following-sibling::p').text
    except:
        ask=''
    try:
        revenue=driver.find_element(By.XPATH,'//p[text()="Revenue"]/following-sibling::p').text
    except:
        revenue=''
    try:
        ebitda=driver.find_element(By.XPATH,'//p[text()="EBITDA"]/following-sibling::p').text
    except:
        ebitda=''
    try:
        cashflow=driver.find_element(By.XPATH,'//p[text()="SDE"]/following-sibling::p').text
    except:
        cashflow='N/A'
    try:
        netincome=driver.find_element(By.XPATH,'//p[text()="Asking Png-sibling::p').text
    except:
        netincome='N/A'

    listed=driver.find_elements(By.XPATH,'//h2[text()="Listed by"]/following-sibling::div[1]//div//p')
    listedby=''
    listedbyfirm=''
    for i in listed:
        if 'chakra-text css-0' in i .get_attribute('class'):

            try:
                listedby=i.text
            except:
                listedby=''


        if "chakra-text css-chfit7"  in i.get_attribute('class'):
            try:
                listedbyfirm=i.text
            except:
                listedbyfirm=''
    try:
        # sourcelink=driver.find_element(By.XPATH,'//a[@class="chakra-link css-10qsrqw"]/button[contains(text(),"View")]/..').get_attribute('href')
        sourcelink=WebDriverWait(driver,4).until(EC.element_to_be_clickable((By.XPATH, '(//a[@class="chakra-link css-10qsrqw"]/button[contains(text(),"View")]/..)[1]')))
        link=sourcelink.get_attribute('href')
    except Exception as e:
        import traceback
        traceback.print_exc()
        link='N/A'
    source='Kumo'
    current_datetime = datetime.now(pytz.utc)

    # Convert to Eastern Daylight Time (EDT)
    eastern = pytz.timezone("US/Eastern")
    current_datetime_edt = current_datetime.astimezone(eastern)

    # Format the date as mm/dd/yy
    formatted_date = current_datetime_edt.strftime("%m-%d-%y")

    # print ([title,city,state,country,driver.current_url,industry,desc,'','',listedbyfirm,listedby,ask,revenue,ebitda,cashflow,netincome])
    last=[title,city,state,country,driver.current_url,industry,source,desc,listedbyfirm,listedby,'N/A','N/A',ask,revenue,cashflow,netincome,ebitda,formatted_date,'N/A',link]
    newval_count+=1

    if newval_count == 1:
        save_last(last)

    with open(csvfile,'a',newline='', encoding='utf-8')as  f:
        writer=csv.writer(f)
        if title != '':
            writer.writerow([title,city,state,country,driver.current_url,industry,source,desc,listedbyfirm,listedby,'N/A','N/A',ask,revenue,cashflow,netincome,ebitda,formatted_date,'N/A',link]) 
    


# Close the webdriver
driver.quit()
