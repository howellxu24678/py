# -*- coding: utf-8 -*-
__author__ = 'xujh'


from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import os
import datetime

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 5, 0.5)
price_locator = (By.CLASS_NAME, "avail-fare-price")

driver.get(r'https://booking.airasia.com/Flight/Select?s=False&o1=HKG&d1=DMK&ADT=1&dd1=2017-07-02&mon=true')
wait.until(EC.presence_of_element_located(price_locator))

driver.get(driver.find_element_by_xpath("//li[@class='not-active'][4]//a").get_attribute("href"))
wait.until(EC.presence_of_element_located(price_locator))

price_element = driver.find_elements(*price_locator)

# : price_element[0].text.split(' ')[0].encode("utf-8")
# Out[26]: '1,058.50'
# In[27]: stt = price_element[0].text.split(' ')[0].encode("utf-8")
# In[28]: stt.replace(",", "")
# Out[28]: '1058.50'
