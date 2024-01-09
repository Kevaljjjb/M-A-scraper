import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
import time

# Install ChromeDriver using webdriver_manager
uc.install(ChromeDriverManager().install())


driver = uc.Chrome()

# Open a website
driver.get("https://www.google.com")

# Sleep for a specified time (300 seconds here)
time.sleep(300)

# Optionally, close the driver after use
driver.quit()
