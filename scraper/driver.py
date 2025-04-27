import time
import random
import undetected_chromedriver as uc


class Driver:
    
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
    
    def star(self):
        """Configure undetected chromedriver with network logging"""
        
        if self.driver is not None:
            return print("Driver is already set up. Please reset before reinitializing.")
            
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
        else:
            options.add_argument("--start-maximized")
        
        # Enable performance logging to capture network requests
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        
        # Additional stealth settings
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        # Randomize user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # Initialize undetected chromedriver
        self.driver = uc.Chrome(options=options) 
        
        # Execute stealth scripts
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def end(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
    
    def human_like_delay(self):
        """Random delay to mimic human behavior"""
        time.sleep(random.uniform(0.5, 2.5))