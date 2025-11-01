import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def take_screenshot(url, save_path):
    """
    Navigates to a URL and saves a screenshot of the page.

    Args:
        url (str): The URL of the web page to capture.
        save_path (str): The file path where the screenshot will be saved.
    """
    # Configure Chrome options for headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up the Chrome WebDriver automatically
    service = Service(ChromeDriverManager().install())
    
    driver = None
    try:
        # Initialize the WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to the URL
        driver.get(url)
        
        # Save the screenshot
        driver.save_screenshot(save_path)
        print(f"Screenshot saved to {save_path}")
        
    finally:
        # Ensure the driver is closed
        if driver:
            driver.quit()

if __name__ == '__main__':
    # --- Example Usage ---
    
    # URL of the page to capture
    example_url = "https://arxiv.org/pdf/2211.04346" # Example arXiv abstract page
    
    # Directory to save the screenshot
    output_dir = "screenshots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Path for the output file
    screenshot_file = os.path.join(output_dir, "arxiv_screenshot.png")
    
    # Take the screenshot
    take_screenshot(example_url, screenshot_file)
