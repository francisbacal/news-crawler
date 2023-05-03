from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent

import os, string, random

class Seledriver:
  def __init__(self, name=None, browser="chrome", headless=True, agent=False, timeout=300):
    self.name = name or self.__random_name()
    self.headless = headless
    self.agent = agent

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
    ua = UserAgent()
    user_agent = ua.random

    if browser == "chrome":
      from selenium.webdriver.chrome.options import Options as chromeOptions
      options = chromeOptions()
      options.add_argument('--no-sandbox')

      if self.headless:
        options.add_argument("--headless")

      options.add_argument("--lang=en")
      options.add_argument("--incognito")
      options.add_argument("--start-maximized")
      options.add_experimental_option("excludeSwitches", ["enable-automation"])
      options.add_experimental_option('useAutomationExtension', False)

      if self.agent:
        options.add_argument("user-agent="+user_agent+"")

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