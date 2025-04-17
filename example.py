from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.selenium.screenshot_manager import ScreenshotManager
from src.ocr.vision_processor import VisionProcessor
import os
import time
import random

def main():
    # Initialize screenshot manager
    with ScreenshotManager() as screenshot_mgr:
        url = "https://www.bet365.mx/"
        
        try:
            print("Attempting to access betting site...")
            screenshot_mgr.driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            # Accept cookies if present
            try:
                cookie_button = WebDriverWait(screenshot_mgr.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar todas')]"))
                )
                cookie_button.click()
                print("Accepted cookies")
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                print("No cookie banner found or already accepted")
            
            # Wait for and click Liga MX in the sidebar
            try:
                # First wait for the sidebar to be visible
                sidebar = WebDriverWait(screenshot_mgr.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'sidebar')]"))
                )
                print("Found sidebar")
                
                # Then find and click Liga MX
                liga_mx = WebDriverWait(screenshot_mgr.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Liga MX')]"))
                )
                liga_mx.click()
                print("Clicked on Liga MX")
                
                # Wait for content to load
                time.sleep(random.uniform(3, 5))
                
                # Take full page screenshot
                print("Taking screenshot of full Liga MX section...")
                full_page = screenshot_mgr.take_screenshot(
                    url=None,
                    element_selector=None,
                    filename="liga_mx_full.png"
                )
                if full_page:
                    print(f"Full page screenshot saved to: {full_page}")
                
                # Wait for the match container to be present
                print("\nLooking for matches container...")
                matches_container = WebDriverWait(screenshot_mgr.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'sgl-MarketFixtureDetailsLabel')]"))
                )
                
                # Get all match rows
                time.sleep(2)  # Give extra time for all matches to load
                match_rows = screenshot_mgr.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'sgl-MarketFixtureDetailsLabel')]/ancestor::div[contains(@class, 'gl-Market_General')]"
                )
                
                print(f"Found {len(match_rows)} matches")
                
                # Process each match
                for idx, match in enumerate(match_rows):
                    try:
                        # Scroll the match into view
                        screenshot_mgr.driver.execute_script(
                            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                            match
                        )
                        time.sleep(random.uniform(1, 2))
                        
                        # Get match details
                        teams = match.find_elements(By.XPATH, ".//div[contains(@class, 'rcl-ParticipantFixtureDetails_Team')]")
                        time_element = match.find_elements(By.XPATH, ".//div[contains(@class, 'rcl-ParticipantFixtureDetails_TimeAndDate')]")
                        
                        if teams and time_element:
                            print(f"\nMatch {idx + 1} details:")
                            print(f"Time: {time_element[0].text if time_element else 'N/A'}")
                            for team in teams:
                                print(f"Team: {team.text}")
                        
                        # Take screenshot of this specific match
                        match_file = f"match_{idx + 1}.png"
                        match.screenshot(os.path.join(screenshot_mgr.output_dir, match_file))
                        print(f"Saved match screenshot to: {match_file}")
                        
                    except Exception as e:
                        print(f"Error processing match {idx + 1}: {str(e)}")
                
            except Exception as e:
                print(f"Error during navigation or match finding: {str(e)}")
            
            print(f"\nFinal URL: {screenshot_mgr.driver.current_url}")
            print(f"Page title: {screenshot_mgr.driver.title}")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            if hasattr(screenshot_mgr, 'driver'):
                print(f"Current URL: {screenshot_mgr.driver.current_url}")
                print(f"Page source length: {len(screenshot_mgr.driver.page_source)}")

if __name__ == "__main__":
    main() 