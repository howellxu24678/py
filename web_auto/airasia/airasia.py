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

def get_filename():
    return "airasia_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"

def write_file(_d):
    if len(_d) < 1:
        return

    _dir = os.path.join(os.getcwd(), 'lowest_price')
    if not os.path.isdir(_dir):
        os.mkdir(_dir)
        
    file_path = os.path.join(_dir, get_filename())
    fpy = open(file_path, 'w')

    for k,v in _d.items():
        line = "date:%s lowest price:%.2f" % (k,v)
        fpy.write(line)
        fpy.write("\n")

    fpy.close()


def get_lowest_price(_begin_date, _src, _dst, _count):
    try:
        d = {}
        wait = WebDriverWait(driver, 5)
        date_locator = (By.XPATH, "//li[@class='active']//h3[@class='low-fare-date']")
        price_locator = (By.XPATH, "//div[@class='avail-fare-price']")
        next_url_locator = (By.XPATH, "//li[@class='not-active'][4]//a")

        driver.get(r'http://www.airasia.com/cn/zh/home.page')
        #title_contains(u'亚洲')
        wait.until(EC.presence_of_element_located((By.XPATH, "//title")))

        url_ = r'https://booking.airasia.com/Flight/Select?o1=%s&d1=%s&dd1=%s&cc=CNY' % (_src, _dst, _begin_date)
        for i in range(_count):
            print 'get url:%s' % url_
            driver.get(url_)

            wait.until(EC.presence_of_element_located(date_locator))
            #wait.until(EC.)
            _date = driver.find_element(*date_locator).text.encode('utf-8')

            #wait.until(EC.presence_of_element_located(price_locator))
            price_list = [float(x.text.split(' ')[0].encode('utf-8').replace('≈', '').replace(',', ''))
                          for x in driver.find_elements(*price_locator)]
            d[_date] = min(price_list)

            #wait.until(EC.presence_of_element_located(next_url_locator))
            url_ = driver.find_element(*next_url_locator).get_attribute("href")

        print d
        #write_file(d)
    except BaseException, e:
        print e
        driver.close()
    finally:
        write_file(d)

get_lowest_price('2017-06-08', 'HKG', 'DMK', 100)
driver.close()



#     #https://booking.airasia.com/Flight/Select?o1=HKG&d1=DMK&culture=zh-CN&dd1=2017-07-02&ADT=1&CHD=0&inl=0&cc=HKD
#     #driver.get(r'https://booking.airasia.com/Flight/Select?s=False&o1=HKG&d1=DMK&ADT=1&dd1=2017-07-02&mon=true')
#     driver.get(r'https://booking.airasia.com/Flight/Select?o1=HKG&d1=DMK&culture=zh-CN&dd1=2017-07-02&ADT=1&CHD=0&inl=0&cc=HKD')
#     wait.until(EC.presence_of_element_located(date_locator))
#     print 'date %s' % driver.find_element(*date_locator)
#     #wait.until(EC.presence_of_element_located(price_locator))
#
#     driver.get(driver.find_element_by_xpath("//li[@class='not-active'][4]//a").get_attribute("href"))
#     wait.until(EC.presence_of_element_located(price_locator))
#
#     price_element = driver.find_elements(*price_locator)
#
# # : price_element[0].text.split(' ')[0].encode("utf-8")
# # Out[26]: '1,058.50'
# # In[27]: stt = price_element[0].text.split(' ')[0].encode("utf-8")
# # In[28]: stt.replace(",", "")
# # Out[28]: '1058.50'
