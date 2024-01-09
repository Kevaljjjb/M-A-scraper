import  csv
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import pytz
import time

mainfile="output.csv"
last_csv='./config/last_linkbusiness.csv'
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
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(),"Listing:")]/preceding-sibling::h1')))
            try:
                title = driver.find_element(By.XPATH, '//span[contains(text(),"Listing:")]/preceding-sibling::h1').text
            except:
                title = 'N/A'

            city = 'N/A'
            state = 'N/A'
            country = 'N/A'
            try:
                location = driver.find_element(By.XPATH, '//label[text()="Location:"]/following-sibling::p').text.strip()
                if ',' in location:
                    city,state=location.split(',')
                else:   
                    state=location
            except Exception as e:
                location = 'N/A'
                print(f"An error occurred: {e}")

            # print(city)
            source='linkbusiness.com'
            try:
                revenue=driver.find_element(By.XPATH, '//label[text()="Sales:"]/following-sibling::p').text
            except:
                revenue='N/A'
            try:
                cashflow=driver.find_element(By.XPATH, '//span[contains(text(), "Cash Flow:")]/following-sibling::b').text
            except:
                cashflow='N/A'

            try:
                inventory=driver.find_element(By.XPATH,'//span[contains(text(), "Inventory:")]/following-sibling::b').text
            except:
                inventory='N/A'
            try:
                ebitda=driver.find_element(By.XPATH,'//label[text()="Profit*:"]/following-sibling::p').text
            except:
                ebitda='N/A'
            try:
                description=driver.find_element(By.XPATH,'//span[@itemprop="description"]').text
            except:
                description = 'N/A'
            try:
                listedby=driver.find_element(By.XPATH,'//a[@class="borkerLink"]').text
            except:
                listedby='N/A'
            try:
                listedby_firm=driver.find_element(By.XPATH,'//h3[@class="media-heading"]//a/text()')[0]
                listedby_firm=''.join(listedby_firm).strip()
            except:
                listedby_firm='N/A'
            try:
                main_phone=driver.find_element(By.XPATH,'//label[contains(text(),"Phone:")]/..').text
                mobile=driver.find_element(By.XPATH,'//label[contains(text(),"Mobile:")]/..').text
                phone=main_phone+"\n"+mobile
                        
            except:
                phone='N/A'
            try:
                mail=driver.find_element(By.XPATH,'//label[contains(text(),"Email:")]/following-sibling::a').text
            except:
                mail='N/A'
            try:
                industry=driver.find_element(By.XPATH,'//label[text()="Industry:"]/following-sibling::p').text
            except:
                industry='N/A'
            try:
                ask=driver.find_element(By.XPATH,'//label[text()="Price:"]/following-sibling::p').text
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
        #   w.writerow(["URL"])
          for i in data:
            w.writerow([i])     


def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument(f'--headless')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    wait = WebDriverWait(driver, 10)
    urls=[]
    driver.get('''https://linkbusiness.com/businesses-for-sale/search?locationNames=%20Alabama%2C%20Arizona%2C%20Arkansas%2C%20California%2C%20Central%20States%2C%20Colorado%2C%20Connecticut%2C%20Cross%2C%20East%20Coast%20States%2C%20Hawaii%2C%20Illinois%2C%20Indiana%2C%20International%20Opportunity%2C%20Kentucky%2C%20Midwest%2C%20Mississippi%2C%20Mississippi%2C%20Missouri%2C%20Nevada%2C%20New%20Jersey%2C%20New%20York%2C%20North%20Carolina%2C%20Ontario%2C%20Other%2C%20Other%20States%2C%20Pennsylvania%2C%20Relocatable%2C%20Relocatable%20%2C%20South%20Central%20US%2C%20Tennessee%2C%20Texas%2C%20Undisclosed%2C%20United%20States%2C%20Washington%2C%20Western%20States&subLocationNames=Acres%20Green%2CAdams%20County%2CAetna%20Estates%2CAguilar%2CAir%20Force%20Academy%2CAkron%2CAlamosa%2CAlamosa%20East%2CAlbany%2CAlgoma%2CAllenspark%2CAlma%2CAlpine%2CAngleton%2CAntonito%2CApplewood%2CArboles%20and%20Grand%20Lake%2CAristocrat%20Ranchettes%2CArriba%2CArvada%2CAspen%2CAspen%20Park%2CAtwood%2CAult%2CAurora%2CAvon%2CAvondale%2CBark%20Ranch%2CBasalt%2CBattlement%20Mesa%2CBayfield%2CBennett%2CBergen%2CBerkley%2CBerks%20County%2CBerthoud%2CBethune%2CBeulah%20Valley%2CBlack%20Forest%2CBlack%20Hawk%20and%20East%20Pleasant%20View%2CBlanca%2CBlende%2CBlue%20River%2CBlue%20Sky%20and%20Valmont%2CBlue%20Valley%2CBonanza%2CBonanza%20Mountain%20Estates%2C%20Seibert%2C%20and%20Mountain%20Meadows%2CBoone%2CBoulder%2CBow%20Mar%2CBrandon%2CBrant%2CBreckenridge%2CBrenham%2CBriggsdale%2CBrighton%2CBronx%2CBrook%20Forest%20and%20Altona%2CBrooklyn%2CBrookside%2CBroomfield%2CBrush%2CBucks%20County%2CBuena%20Vista%2CBurlington%2CByers%2CCalhan%2CCalifornia%2CCa%C3%B1on%20City%2CCapulin%2CCarbondale%2CCascade-Chipita%20Park%2CCastle%20Pines%2CCastle%20Pines%20Village%2CCastle%20Rock%2CCathedral%2CCatherine%2CCattle%20Creek%2CCedaredge%2CCentennial%2CCenter%2CCentral%20Arizona%2CCentral%20Coast%20%2CCentral%20Colorado%2CCentral%20Illinois%2CCentral%20PA%2CCentral%20Pennsylvania%2CCentral%20Pennsylvania%2CCentral%20Texas%2CCentre%20County%2CChacra%2CCharlotte%2CCheraw%2CCherry%20Creek%2CCherry%20Hills%20Village%2CChester%20County%2CCheyenne%20Wells%2CCimarron%20Hills%2CCity%20of%20Creede%2CClay%2CClifton%2CCoachella%20Valley%20and%20Desert%20Cities%2CCoal%20Creek%2CCoal%20Creek%20CDP%2CCoaldale%2CCoastal%20Plain%2CCochrane%2CCollbran%2CColona%2CColorado%20City%20and%20Leadville%20North%2CColorado%20Springs%2CColumbia%20County%2CColumbine%2CColumbine%20Valley%2CComanche%20Creek%2CCommerce%20City%2CCope%20and%20Idalia%2CCopper%20Mountain%2CCortez%2CCotopaxi%20and%20Two%20Buttes%2CCraig%2CCraighead%2CCrawford%2CCrested%20Butte%2CCripple%20Creek%2CCrook%2CCumberland%20County%2CDacono%2CDakota%20Ridge%2CDallas%2CDallas-Fort%20Worth%2CDauphin%20County%2CDavidson%20County%2CDe%20Beque%2CDeer%20Trail%2CDel%20Norte%2CDelawar%20County%2CDelta%2CDenver%2CDerby%2CDillon%2CDinosaur%2CDivide%2C%20Cokedale%2C%20and%20Seven%20Hills%2CDolores%2CDotsero%2CDove%20Creek%2CDove%20Valley%2CDownieville-Lawson-Dumont%2CDurango%2CDurham%2CDutchess%20County%2CEads%2CEagle%2CEast%20Africa%2CEast%20Coast%20States%2CEast%20Texas%2CEastern%20PA%2CEastern%20Pennsylvania%2CEastern%20Plains%2CEastern%20States%2CEaton%2CEcho%20Hills%2CEckley%2CEdgewater%2CEdwards%2CEl%20Jebel%2CEl%20Moro%2CElbert%2CEldora%2CEldorado%20Springs%2CElgin%2CElizabeth%2CEllicott%2CEnglewood%2CErie%2CEssex%2CEstes%20Park%2CEvans%2CEvergreen%2CFairfield%2CFairmount%2CFairplay%2CFederal%20Heights%2CFirestone%2CFlagler%2CFleming%2CFlorence%2CFlorissant%2CFloyd%20Hill%2CFort%20Carson%2CFort%20Collins%2CFort%20Garland%2CFort%20Lupton%2CFort%20Morgan%2CFort%20Worth%2CFountain%2CFour%20Square%20Mile%2CFowler%2CFoxfield%2CFranklin%20County%2CFranklin%20County%2CFranktown%2CFraser%2CFrederick%2CFrisco%2CFrontenac%2CFruita%2CFruitvale%2CGalveston%2CGardner%2CGenesee%2CGenoa%2CGeorgetown%2CGerrard%2CGilcrest%2CGlendale%20city%2CGleneagle%2CGlenwood%20Springs%2CGolden%2CGoldfield%2CGranada%2CGranby%2CGrand%20Junction%2CGrand%20View%20Estates%2CGreater%20Bakersfield%20Area%2CGreater%20Chicago%20Area%2CGreater%20Fresno%20Area%2CGreater%20Kansas%20City%20Area%2CGreater%20Lake%20Tahoe%20Area%2CGreater%20Sacramento%20Area%2CGreater%20San%20Francisco%20Bay%20Area%2CGreater%20San%20Joaquin%20Valley%20Area%2CGreater%20St.%20Charles%20County%2CGreater%20St.%20Louis%20Area%2CGreater%20St.%20Louis%20Area%2CGreeley%2CGreen%20Mountain%20Falls%20and%20Stratton%2CGreene%2CGreenwood%20Village%2CGrey%2CGrover%20and%20Amherst%2CGunbarrel%2CGunnison%2CGypsum%2CHaldimand%2CHalton%2CHamilton%2CHartman%2CHastings%2CHasty%2CHaxtun%2CHayden%2CHeeney%2CHempstead%2CHidden%20Lake%2CHighlands%20Ranch%2CHillrose%2CHoehne%2CHolly%2CHolly%20Hills%2CHolyoke%2CHooper%2CHot%20Sulphur%20Springs%2CHotchkiss%2CHouston%2CHoward%2CHudson%2CHugo%2CHumboldt%20County%2CIdaho%20Springs%2CIdledale%2CIgnacio%2CIliff%20and%20Lazear%2CIllinois%2CImperial%20County%2CIndependence%2CIndian%20Hills%2CInternational%2CInverness%2CJamestown%20and%20Garden%20City%2CJansen%2CJoes%2CJohnson%20Village%2CJohnstown%2CJulesburg%2CJuniata%20County%2CKawartha%20Lakes%2CKeenesburg%2CKen%20Caryl%2CKenora%2CKentucky%2CKersey%2CKeystone%20and%20Upper%20Bear%20Creek%2CKiowa%2CKirk%2CKit%20Carson%2CKittredge%2CKremmling%2CLa%20Jara%2CLa%20Junta%2CLa%20Junta%20Gardens%2CLa%20Salle%2CLa%20Veta%2CLafayette%2CLaird%2CLake%20City%2CLakeside%2CLakewood%2CLamar%2CLambton%2CLancaster%20County%2CLaporte%2CLarkspur%20and%20Peetz%2CLas%20Animas%2CLawrence%2CLazy%20Acres%2CLeadville%2CLebanon%20County%2CLeeds%20and%20Grenville%2CLewis%2CLiberty%2CLimon%2CLincoln%20Park%2CLittleton%2CLochbuie%2CLog%20Lane%20Village%2CLoghill%20Village%2CLoma%2CLone%20Tree%2CLong%20Island%2CLongmont%2CLos%20Angeles%20County%2CLouisville%2CLouviers%20and%20Morrison%2CLoveland%2CLycoming%20County%2CLynn%2CLyons%2CMamaroneck%2CManassa%2CMancos%2CManhattan%2CManitou%20Springs%2CManzanola%2CMarble%20and%20Brick%20Center%2CMarvel%2CMatheson%2CMaybell%2CMaysville%2CMcClave%2C%20Sedalia%2C%20and%20Campo%2CMcCoy%2CMead%2CMeeker%2CMemphis%20Metro%2CMeridian%2CMeridian%20Village%2CMerino%2CMetro%20Phoenix%20Area%2CMid-Atlantic%20States%2CMiddlesex%2CMidland%2CMifflin%20County%2CMilliken%2CMinturn%2CMoffat%2CMonte%20Vista%2CMontezuma%2CMontgomery%20County%2CMontour%20County%2CMontrose%2CMonument%2CMorgan%20Heights%2CMount%20Crested%20Butte%2CMountain%20Area%2CMountain%20View%2CMountain%20Village%2CMulford%2CNassau%2CNathrop%2CNaturita%2CNederland%2CNew%20Castle%2CNew%20York%20City%2CNiagara%2CNipissing%2CNiwot%2CNo%20Name%2CNorfolk%2CNorth%20La%20Junta%2CNorth%20Texas%2CNorth%20Texas%2CNorth%20Washington%2CNortheastern%20Pennsylvania%2CNorthern%20Arizona%2CNorthern%20California%2CNorthern%20Colorado%2CNorthern%20Missouri%2CNorthern%20Nevada%2CNorthern%20Nevada%2CNorthern%20St.%20Louis%2CNorthglenn%2CNorthumberland%20County%2CNorthwest%20Alabama%2CNorwood%2CNucla%2CNunn%2COak%20Creek%2COlathe%2COlney%20Springs%2COphir%20and%20Gold%20Hill%2COrange%20County%2COrange%20County%2COrchard%2COrchard%20City%2COrchard%20Mesa%2COrdway%2COttawa%2COuray%2COvid%2COxford%2CPadroni%20and%20Kim%2CPagosa%20Springs%2CPalisade%2CPalmer%20Lake%2CPaoli%2CPaonia%2CParachute%2CParagon%20Estates%20and%20Central%20City%2CPark%20Center%2CParker%2CParshall%2CPeekskill%2CPeel%2CPenrose%2CPeoria%2CPerry%20County%2CPerry%20Park%2CPerth%2CPeterborough%2CPhiladelphia%20County%2CPhippsburg%2CPhoenix%2CPiedmont%20Triad%2CPiedra%20and%20Conejos%2CPierce%2CPine%20Brook%20Hill%2CPine%20Valley%2CPitkin%2CPlacerville%2CPlatteville%2CPoinsett%2CPoncha%20Springs%2CPonderosa%20Park%2CPortland%2CPoughkeepsie%2CPrescott%20and%20Russell%2CPrince%20Edward%2CPritchett%2CPueblo%2CPueblo%20West%2CPutnam%20County%2CQueens%2CRandolph%2CRangely%2CRaymer%20%28New%20Raymer%29%2C%20Ramah%2C%20and%20Glendale%2CRed%20Cliff%2CRed%20Feather%20Lakes%2CRedlands%2CRedstone%2CRedvale%2CRenfrew%2CRico%2CRidgway%2CRifle%2CRiverside%20County%2CRock%20Creek%20Park%2CRockland%20County%2CRockvale%2CRocky%20Ford%2CRocky%20Mountain%20Region%2CRollinsville%2CRomeo%2CRoxborough%20Park%2CRye%2CSaddle%20Ridge%20and%20Crisman%2CSaguache%2CSalida%2CSalt%20Creek%2CSan%20Acacio%2CSan%20Antonio%2CSan%20Bernardino%20County%2CSan%20Diego%20County%2CSan%20Fernando%20Valley%2CSan%20Luis%2CSandhills%2CSanford%2CSchuylkill%2CSecurity-Widefield%2CSedgwick%2CSegundo%2CSeverance%2CSharp%2CShaw%20Heights%2CSheridan%2CSheridan%20Lake%2C%20Arapahoe%2C%20and%20Branson%2CSherrelwood%2CSierra%20Ridge%2CSilt%2CSilver%20Cliff%2CSilver%20Plume%2CSilverthorne%2CSilverton%2CSimcoe%2CSimla%2CSmeltertown%20and%20Haswell%2CSnowmass%20Village%2CSnyder%2CSnyder%20County%2CSomerset%2CSouth%20Africa%2CSouth%20Central%20US%2CSouth%20Fork%2CSouth%20Texas%2CSouthern%20Arizona%2CSouthern%20California%2CSouthern%20Colorado%2CSouthern%20Illinois%2CSouthern%20Missouri%2CSouthern%20Nevada%2CSouthern%20Ute%2CSouthwestern%20Colorado%2CSpain%2CSpain%2CSpringfield%2CSt.%20Ann%20Highlands%2CSt.%20Francis%2CSt.%20Mary%27s%2CStarkville%2CStaten%20Island%2CSteamboat%20Springs%2CStepping%20Stone%2CSterling%2CSterling%20Ranch%20and%20Otis%2CStonegate%2CStonewall%20Gap%20and%20Sawpit%2CStormont%2C%20Dundas%20and%20Glengarry%2CStrasburg%2CStratmoor%2CSudbury%2CSuffolk%2CSugar%20City%2CSugarland%2CSugarloaf%2CSunshine%2CSuperior%2CSwink%2CTabernash%2CTall%20Timber%2CTelluride%2CTenafly%2CThe%20Pinery%2CThe%20Woodlands%2CThornton%2CThunder%20Bay%2CTimiskaming%2CTimnath%2CTodd%20Creek%2CToronto%2CTowaoc%2CTowner%2CTrail%20Side%2C%20Crestone%2C%20and%20Jackson%20Lake%2CTriangle%20Area%2CTrinidad%2CTri-State%20Area%2CTwin%20Lakes%20and%20Crowley%2CTwin%20Lakes%20CDP%2CUndisclosed%2CUnion%20County%2CUnited%20Kingdom%2CUnited%20Kingdom%2CUpper%20Witter%20Gulch%2CVail%2CVentura%20%26%20Santa%20Barbara%20Counties%2CVictor%2CVilas%2CVineland%20and%20Empire%2CVona%2CWake%20County%2CWalden%2CWalsenburg%2CWalsh%2CWard%2CWaterloo%2CWayne%20County%2CWelby%2CWeldona%2CWellington%2CWellington%2CWest%20Pleasant%20View%2CWest%20Texas%2CWestchester%20County%2CWestcliffe%2CWestcreek%2CWestern%20Slope%2CWestminster%2CWeston%2CWestport%2CWheat%20Ridge%2CWiggins%2CWiley%2CWilliamsburg%20and%20Watkins%2CWindsor%2CWinter%20Park%2CWoodland%20Park%2CWoodmoor%2CWoodruff%2CWoody%20Creek%2CWray%2CYampa%2CYork%2CYork%20County%2CYuma&salesPriceFrom=4%2C000%2C000&sortBy=FeaturedFirst&page=1&searchByName=True&commissionSplit=AllListings''')
    time.sleep(3)
    while True:
        # Find and store href and title data
        listings = driver.find_elements(By.XPATH, '//a[text()="VIEW LISTING"]')
        for listing in listings:
            # title = listing.get_attribute('title')
            href = listing.get_attribute('href')
            # csv_writer.writerow([title, href])
            urls.append(href)
        
        # Find next page button and click it
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        try :
            next_button = driver.find_element(By.XPATH, '//a[text()="Next"]')
            actions = ActionChains(driver)
            actions.move_to_element(next_button).click().perform()
            
            driver.implicitly_wait(5)
        except:
            break
    return urls

if __name__ == "__main__":
    allhref=main()
    # print(allhref)
    unique_urls = set(allhref)-set(last) 
    driver_path = "./config/chromedriver.exe"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
    if len(unique_urls)>0:
        fetch_data(driver,unique_urls)
        update_first(list(unique_urls))