import os
from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains

class Scraper:
    
    def __init__(
            self, 
            email: str, 
            password: str, 
            group_file: str, 
            show: bool = False
        ) -> None:
        
        if os.path.exists(group_file):
            self.group_file = group_file
        else:
            raise FileNotFoundError(f"Group file {group_file} not found")
        
        self.email = email
        self.password = password
        self.show = show
        self.driver = None
        
        self.status: bool = False
        self.status_page: bool = False
    
    def start(self) -> None:
        
        if self.status:
            print("There is already a connection")
            return
        
        options = uc.ChromeOptions()
        
        if not self.show:
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            options.add_experimental_option('prefs', {'intl.accept_languages': 'es'})
            self.driver = uc.Chrome(headless=False, options=options, version_main=120)
        
        else:
            options.add_argument("--start-maximized")
            self.driver = uc.Chrome(options=options)
            self.driver.maximize_window()
        
        self.status = True
        return
    
    def end(self) -> None:
        
        if not self.status:
            print("the connection is over")
            return
        
        self.driver.quit()
        return
        
    def clik(self, xpath: str) -> None:
        WebDriverWait(self.driver, 60).\
            until(expected_conditions.element_to_be_clickable((By.XPATH, xpath))).click()
        return
        
    def login(self) -> None:
        
        if self.status_page:
            print("The user is already logged in")
            return
        
        self.driver.get('https://www.facebook.com/')
        sleep(2)
        
        # It is recorded
        WebDriverWait(self.driver, 60).until(expected_conditions.presence_of_element_located((By.ID, 'email'))).send_keys(self.email)
        sleep(2)
        self.driver.find_element(By.ID, 'pass').send_keys(self.password)
        sleep(2)
        self.clik('//button[@type="submit"]')
        self.status_page = True
        return
    
    def logout(self) -> None:
        
        if not self.status_page:
            print("The user is already logout in")
            return
        
        self.clik('//*[@id="mount_0_0_8Y"]/div/div[1]/div/div[2]/div[5]/div[1]/span')
        sleep(2)
        self.clik('//*[@id="mount_0_0_8Y"]/div/div[1]/div/div[2]/div[5]/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div[1]/div/div/div[1]/div[2]/div/div[5]')
        self.status_page = False
        return
    
    def search_group(self, link: str) -> None:
        self.driver.get(link)