# -*- coding: utf-8 -*-
__author__ = 'xujh'


import multiprocessing
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import os
import datetime


#global driver


def get_filename(_begin_date, _src, _dst):
    return "airasia_%s%s%s_%s.txt" % \
           (_begin_date, _src, _dst, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))


def write_file(_begin_date, _src, _dst, _l):
    if len(_l) < 1:
        return

    _dir = os.path.join(os.getcwd(), 'lowest_price')
    if not os.path.isdir(_dir):
        os.mkdir(_dir)

    file_path = os.path.join(_dir, get_filename(_begin_date, _src, _dst))
    fpy = open(file_path, 'w')

    for i in _l:
        line = "date:%s lowest price:%.2f" % (i[0], i[1])
        fpy.write(line)
        fpy.write("\n")

    # 对value进行排序
    _l_sorted = sorted(_l, lambda x, y: cmp(x[1], y[1]))
    line = "the lowest price during the quantum is date:%s, price:%.2f" \
           % (_l_sorted[0][0], _l_sorted[0][1])
    fpy.write(line)
    fpy.write("\n")
    fpy.close()

def gen_url( _src, _dst, _date):
    return (_date, r'https://booking.airasia.com/Flight/Select?o1=%s&d1=%s&dd1=%s&cc=CNY' % (_src, _dst, _date))

def gen_urls(_begin_date, _src, _dst, _count):
    begin_date = datetime.datetime.strptime(_begin_date, '%Y-%m-%d')
    return [gen_url(_src, _dst, (begin_date + datetime.timedelta(days = x)).strftime('%Y-%m-%d')) for x in range(_count)]

def get_lowest_price(_arg):
    try:
        _date, _url = _arg
        global driver
        wait = WebDriverWait(driver, 5)
        price_locator = (By.XPATH, "//div[@class='avail-fare-price']")
        driver.get(_url)
        wait.until(EC.presence_of_element_located(price_locator))
        price_list = [float(x.text.split(' ')[0].encode('utf-8').replace('≈', '').replace(',', ''))
                      for x in driver.find_elements(*price_locator)]
        return (_date, min(price_list))
    except BaseException, e:
        print e
        # driver.close()
        # driver.quit()
    # finally:
    #     write_file(_begin_date, _src, _dst, l)

def get_lowest_price2(_arg):
    pass

def init():
    try:
        global driver
        # 禁用图片加载
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chromeOptions.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(chrome_options=chromeOptions)
        driver.get(r'http://www.airasia.com/cn/zh/home.page')
        # title_contains(u'亚洲')
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//title")))
    except BaseException, e:
        print e

def init2():
    try:
        global driver
        # 禁用图片加载
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chromeOptions.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(chrome_options=chromeOptions)
        driver.get(r'http://www.baidu.com')
        # # title_contains(u'亚洲')
        # WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//title")))
    except BaseException, e:
        print e


def close(x):
    global driver
    driver.close()
    driver.quit()


def get_lowest_price_multi(_begin_date, _src, _dst, _count):
    try:

        #pool = multiprocessing.Pool(processes=multiprocessing.cpu_count(), initializer=init)
        cpu_count = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=cpu_count, initializer=init2)
        ll = pool.map(get_lowest_price2, gen_urls(_begin_date, _src, _dst, _count))
        print ll
        pool.map(close, [x for x in range(cpu_count)])

        print "Started processes"

        pool.terminate()
        #pool.close()
        pool.join()
        print "Subprocess done."

    except BaseException, e:
        print e



if __name__ == '__main__':
    # 香港：HKG
    # 曼谷廊曼：DMK
    # 深圳：SZX
    get_lowest_price_multi('2017-06-15', 'SZX', 'DMK', 10)