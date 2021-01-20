from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import os, string, random

class Seledriver:
  def __init__(self, name=None, browser="chrome", headless=True, timeout=300):
    self.name = name or self.__random_name()
    self.headless = headless

    # INSTANTIATE SELENIUM DRIVER

    if browser == "fox":
      options = self.__set_driver_options(headless=self.headless, browser=browser)
      driver = webdriver.Firefox(options=options)
      driver.set_page_load_timeout(timeout)  

    else:
      options = self.__set_driver_options(headless=self.headless, browser="chrome")
      driver = webdriver.Chrome(options=options)
      driver.set_page_load_timeout(timeout)
    
    self.browser = driver
  
  def __set_driver_options(self, headless=True, browser="chrome"):
  
    if browser == "chrome":
      from selenium.webdriver.chrome.options import Options as chromeOptions
      user_agent_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
          ]
      options = chromeOptions()
      options.add_argument('--no-sandbox')

      if self.headless:
        options.add_argument("--headless")

      options.add_argument("--lang=en")
      options.add_argument("--incognito")
      options.add_argument("--start-maximized")
      options.add_experimental_option("excludeSwitches", ["enable-automation"])
      options.add_experimental_option('useAutomationExtension', False)

    if browser == "fox":
      from selenium.webdriver.firefox.options import Options as foxOptions
      options = foxOptions()
      if headless:
        options.headless = True
      
      options.add_argument('-private')

    return options
  
  def __random_name(self):
    alpha_strings = string.ascii_lowercase + string.digits
    result = ''.join((random.choice(alpha_strings) for i in range(8)))

    return str(result)
  
  def wait(self, driver, wait_time):
    wait_time = wait_time or 10
    
    return WebDriverWait(driver, wait_time)