from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException
import os
from datetime import datetime
import sys
import time
import random

class ScreenshotManager:
    def __init__(self, output_dir="screenshots"):
        """Initialize the Screenshot Manager with Chrome options"""
        self.output_dir = output_dir
        self.setup_output_directory()
        self.setup_driver()
    
    def setup_output_directory(self):
        """Create screenshots directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def setup_driver(self):
        """Setup Chrome driver with custom options"""
        try:
            chrome_options = Options()
            # Comment out headless mode for testing
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Enhanced anti-detection measures
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            # Add more realistic user agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36')
            
            # Add language preferences
            chrome_options.add_argument('--lang=es-MX')
            
            # Add additional preferences
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_settings.popups": 0,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            })
            
            # Get the ChromeDriver path and ensure it points to the executable
            driver_path = ChromeDriverManager().install()
            driver_dir = os.path.dirname(driver_path)
            chromedriver_exe = os.path.join(driver_dir, 'chromedriver.exe')
            
            print(f"Looking for ChromeDriver in: {driver_dir}")
            if os.path.exists(chromedriver_exe):
                print(f"Found ChromeDriver executable at: {chromedriver_exe}")
                driver_path = chromedriver_exe
            else:
                print("Searching for chromedriver.exe in directory...")
                for file in os.listdir(driver_dir):
                    if file.endswith('chromedriver.exe'):
                        driver_path = os.path.join(driver_dir, file)
                        print(f"Found ChromeDriver at: {driver_path}")
                        break
            
            # Create the service
            service = Service(executable_path=driver_path)
            
            # Initialize the driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set window size explicitly after creation
            self.driver.set_window_size(1920, 1080)
            
            # Add stealth properties
            self.add_stealth_properties()
            
            print("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            print(f"Error setting up Chrome WebDriver: {str(e)}")
            print(f"Current directory: {os.getcwd()}")
            print("\nTroubleshooting steps:")
            print("1. Make sure Chrome is installed on your system")
            print("2. Check if Chrome version matches the WebDriver version")
            print("3. Try running without headless mode by commenting out the headless argument")
            print(f"4. Check if ChromeDriver exists at: {driver_path}")
            sys.exit(1)
    
    def add_stealth_properties(self):
        """Add various JavaScript properties to make automation less detectable"""
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['es-MX', 'es', 'en-US', 'en']});
            window.chrome = { runtime: {} };
        """)
    
    def random_sleep(self, min_seconds=1, max_seconds=3):
        """Sleep for a random amount of time to mimic human behavior"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def take_screenshot(self, url, element_selector=None, filename=None):
        """Take a screenshot of a webpage or specific element"""
        try:
            if url:
                print(f"Attempting to access URL: {url}")
                self.driver.get(url)
                print("Successfully loaded the page")
                
                # Random sleep to mimic human behavior
                self.random_sleep(2, 4)
                
                # Accept cookies if present
                try:
                    cookie_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar todas')]"))
                    )
                    cookie_button.click()
                    print("Accepted cookies")
                    self.random_sleep()
                except:
                    print("No cookie banner found or already accepted")
            
            if element_selector:
                print(f"Looking for element with selector: {element_selector[1]}")
                # Wait for element to be visible
                element = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(element_selector)
                )
                # Scroll element into view with smooth behavior
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                self.random_sleep()
                print("Found the element, taking screenshot")
                screenshot = element.screenshot_as_png
            else:
                # Wait for page load
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                print("Page fully loaded, taking full page screenshot")
                screenshot = self.driver.get_screenshot_as_png()
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Save screenshot
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(screenshot)
            
            print(f"Screenshot saved successfully to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            if hasattr(self, 'driver'):
                print(f"Current URL: {self.driver.current_url}")
                print(f"Page source length: {len(self.driver.page_source)}")
            return None
    
    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close() 