import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
import time

# Install ChromeDriver using webdriver_manager
# uc.install(executable_path=ChromeDriverManager().install())

from selenium.webdriver import Chrome


driver = Chrome()
driver.get( 'https://flippa.com/login' )
