from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pytz
import time 
import re
import csv        


last_csv='./config/last_dealfeed.csv'

last=[]
with open(last_csv, 'r') as f:
    reader = csv.reader(f)
    next(reader, None)
    for i in reader :
        last.append(i[0])

main_file="soft_data.csv"
def get_revenue(cash):
    if '$' in cash:
        value = re.sub(r"[^\d\-+\.]", "", cash)
        # Convert the value to a float.
        value = int(value)
    else:
        value=''
    return value

def fetch_data(driver):
    try:
        try:
            title = driver.find_element(By.XPATH, './h2[not(contains(text(),"Broker Description"))]').text.strip()  #/h2[@class="mt-0" and not(node())]
        except:
            title = 'N/A'

        city = 'N/A'
        state = 'N/A'
        country = 'N/A'
        
        source='dealfeed.com'
        try:
            revenue=get_revenue(driver.find_element(By.XPATH, './/h3[text()="Average Monthly Revenue"]/following-sibling::p').text)
            revenue="$ "+str(revenue*12)
        except:
            revenue='N/A'
        try:
            cashflow=driver.find_element(By.XPATH, '//div[contains(text(),"Cash Flow (per Year) : ")]/span').text
        except:
            cashflow='N/A'

        try:
            inventory=driver.find_element(By.XPATH,'//div[contains(text(),"Inventory")]/following-sibling::div/text()')[0]
            inventory=''.join(inventory).strip()
        except:
            inventory='N/A'
        try:
            ebitda=driver.find_element(By.XPATH,'//div[text()="Gross Income"]/following-sibling::div').text
        except:
            ebitda='N/A'
        try:
            decription= driver.find_element(By.XPATH,'.//p[@class="parag"]').text
        except:
            decription='N/A'
        try:
            listedby=driver.find_element(By.XPATH,'//li[@class="name"]').text
        except:
            listedby='N/A'
        try:
            listedby_firm=driver.find_element(By.XPATH,'//div[@class="ct-personContent"]//h5')[0]
            listedby_firm=''.join(listedby_firm).strip()
        except:
            listedby_firm='N/A'
        try:
            phone=driver.find_element(By.XPATH,'//li[@class="mobile"]').text
        except:
            phone='N/A'
        try:
            mail=driver.find_element(By.XPATH,'//li[@class="email"]').text
        except:
            mail='N/A'
        try:
            industry=driver.find_element(By.XPATH,'//div[contains(text(),"Property Type : ")]/span').text
        except:
            industry='N/A'
        try:
            ask=driver.find_element(By.XPATH,'.//h3[contains(text()," List Price")]/following-sibling::p').text
        except:
            ask='N/A'
        try:
            source_url=driver.find_element(By.XPATH,'.//a[contains(text(),"View Full Listing")]').get_attribute('href')
        except:
            source_url="N/A"
        current_datetime = datetime.now(pytz.utc)

        # Convert to Eastern Daylight Time (EDT)
        eastern = pytz.timezone("US/Eastern")
        current_datetime_edt = current_datetime.astimezone(eastern)

        # Format the date as mm/dd/yy
        formatted_date = current_datetime_edt.strftime("%m/%d/%Y")
        if title != "":
            if source_url not in last:
                data_tocsv=[title,city,state,country,source_url,industry,source,decription,listedby_firm,listedby,phone,mail,ask,revenue,cashflow,inventory,ebitda,formatted_date]
                save_to_csv(data_tocsv)
                update_first(source_url)

    except Exception as e:
        import traceback
        print(f"An error occurred while fetching data from {i}: {str(e)} \n")
        traceback_message = traceback.format_exc()
        print(traceback_message)

def save_to_csv(data):
    with open(main_file,'a',newline='',encoding='utf-8')as f:
        if len(data)>0:
            writer=csv.writer(f)
            writer.writerow(data)

def  update_first(data):
     with open(last_csv,'a',newline='',encoding='utf-8')as f:
            w=csv.writer(f)
            w.writerow([data])  

def main():
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    driver.get("https://thewebsiteflip.com/deal-feed/?&pageNo=1&per_page=10&order_meta_key=_deal_dateOrderListing&orderSort=desc&totalCount=274&niche=&featured=&q=&broker=&monetization=&model=&askingPrice_start=&askingPrice_end=&averageMonthlyNetRevenue_start=84000&averageMonthlyNetRevenue_end=&averageMonthlyNetProfit_start=&averageMonthlyNetProfit_end=&multiple_start=&multiple_end=&age_start=&age_end=&averageMonthlyViews=&already_loaded=true&show_desktop_deal_filter=true&newlisting=&newdeallisting=&agedlisting=&priceincreaselisting=&pricedecreaselisting=&multipleincreaselisting=&multipledecreaselisting=")
    js_code='''btn=document.querySelectorAll(".drop-box");for (let i of btn) {i.click();}'''
    while True:
        driver.execute_script(js_code)
        time.sleep(2)
        trs=driver.find_elements(By.XPATH,'//tr/td[@class="recored-in-details"]')
        for i in trs:
            fetch_data(i)
        try:
            driver.find_element(By.XPATH,'//a[text()=">" and not(@tabindex="-1")]').click()
            time.sleep(4)
        except:
            break

if __name__ == "__main__":
    main()
    