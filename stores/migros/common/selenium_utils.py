from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

class SeleniumDriver:
    def __init__(self):
        # Set Chrome options
        options = Options()
        options.add_argument("--headless")  # Run in headless mode, so no GUI is needed
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Create a new Chrome driver instance
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def get(self, url):
        """Open the webpage at the specified URL"""
        self.driver.get(url)

    def find_element(self, *args, **kwargs):
        """Find a single element by its locator"""
        return self.driver.find_element(*args, **kwargs)

    def find_elements(self, *args, **kwargs):
        """Find multiple elements by their locator"""
        return self.driver.find_elements(*args, **kwargs)

    def get_page_source(self):
        """Return the page source of the current page"""
        return self.driver.page_source

    def quit(self):
        """Quit the driver and close the browser"""
        self.driver.quit()
