import json
import time
import random
import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from . import Driver


class Facebook(Driver):
    
    def __init__(self, username, password, headless=False):
        
        super().__init__(headless)
        
        self.username = username
        self.password = password
        self.network_logs = []
    
    #  -  -  -  -  -  start and end driver -  -  -  -  -  -  -  -  #
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
    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  #
    
    def human_like_delay(self):
        """Random delay to mimic human behavior"""
        time.sleep(random.uniform(0.5, 2.5))
    
    def login(self):
        """Log in to Facebook with human-like behavior"""
        self.driver.get("https://www.facebook.com")
        self.human_like_delay()
        
        try:
            # Accept cookies if the dialog appears
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(string(), 'Allow essential and optional cookies')]"))
            ).click()
            self.human_like_delay()
        except TimeoutException:
            pass  # Cookie dialog didn't appear
            
        # Fill login form with human-like typing
        email_field = self.driver.find_element(By.ID, "email")
        for char in self.username:
            email_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.5))
        
        self.human_like_delay()
        
        password_field = self.driver.find_element(By.ID, "pass")
        for char in self.password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.5))
        
        self.human_like_delay()
        
        login_button = self.driver.find_element(By.NAME, "login")
        login_button.click()
        
        # Wait for login to complete
        try:
            # WebDriverWait(self.driver, 60).until(
            #     EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'on Facebook')]"))
            # )
            print("Login successful")
            return True
        except TimeoutException:
            print("Login failed or took too long")
            return False
    
    def capture_network_requests(self, url):
        """Navigate to a page and capture network requests with random delays"""
        self.driver.get(url)
        self.human_like_delay()
        
        # Clear previous logs
        self.network_logs = []
        
        # Function to process logs
        def process_logs():
            logs = self.driver.get_log("performance")
            for entry in logs:
                try:
                    log = json.loads(entry["message"])["message"]
                    self.network_logs.append(log)
                except ValueError as e:
                    print(e)
                    continue
        
        # Process initial logs
        process_logs()
        
        # the time that the user will do scroll
        SCROLL_COUNT: int = 20
        
        # Scroll to trigger more network requests with random behavior
        for _ in range(SCROLL_COUNT):
            scroll_amount = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self.human_like_delay()
            process_logs()
        
        return self.network_logs
    
    def extract_graphql_data(self):
        """Extract and parse GraphQL requests and responses"""
        graphql_data = []
        
        for log in self.network_logs:
            try:
                
                if "Network.requestWillBeSent" in log["method"]:
                    request = log["params"]["request"]
                    if "graphql" in request["url"].lower() or "query" in request["url"].lower():
                        entry = {
                            "type": "request",
                            "url": request["url"],
                            "method": request["method"],
                            "timestamp": log["params"]["timestamp"],
                            "headers": {k: v for k, v in request["headers"].items() 
                                        if k.lower() not in ["cookie", "authorization"]},
                            "post_data": request.get("postData")
                        }
                        graphql_data.append(entry)
                
                if "Network.responseReceived" in log["method"]:
                    response = log["params"]["response"]
                    url_response = response["url"].lower()
                    
                    if "graphql" in url_response or "query" in url_response:
                        entry = {
                            "type": "response",
                            "url": response["url"],
                            "status": response["status"],
                            "timestamp": log["params"]["timestamp"],
                            "headers": {
                                k: v for k, v in response["headers"].items() 
                                    if k.lower() not in ["set-cookie"]
                            }
                        }
                        
                        # Try to get response body
                        request_id = log["params"]["requestId"]
                        try:
                            response_body = self.driver.execute_cdp_cmd(
                                "Network.getResponseBody", 
                                {"requestId": request_id}
                            )
                            entry["body"] = response_body
                                
                        except ValueError as e:
                            print(e)
                            entry["body"] = "unavailable"
                        
                        graphql_data.append(entry)
            except KeyError as key:
                print(key)
                continue
                
        return graphql_data
    
    def save_data(self, filename: str ="json/facebook_graphql_data.json"):
        """Save captured data to a file"""
        data = self.extract_graphql_data()
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {filename}")