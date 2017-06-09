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

#禁用图片加载
# chromeOptions = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images":2}
# chromeOptions.add_experimental_option("prefs",prefs)
# driver = webdriver.Chrome(chrome_options=chromeOptions)


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


def get_lowest_price(_begin_date, _src, _dst, _day_delta):
    print 'get_lowest_price', _day_delta
    return _day_delta
    # try:
    #     wait = WebDriverWait(driver, 5)
    #     date_locator = (By.XPATH, "//li[@class='active']//h3[@class='low-fare-date']")
    #     price_locator = (By.XPATH, "//div[@class='avail-fare-price']")
    #     next_url_locator = (By.XPATH, "//li[@class='not-active'][4]//a")
    #
    #     driver.get(r'http://www.airasia.com/cn/zh/home.page')
    #     # title_contains(u'亚洲')
    #     wait.until(EC.presence_of_element_located((By.XPATH, "//title")))
    #
    #     url_ = r'https://booking.airasia.com/Flight/Select?o1=%s&d1=%s&dd1=%s&cc=CNY' % (_src, _dst, _begin_date)
    #     for i in range(_count):
    #         print 'get url:%s' % url_
    #         driver.get(url_)
    #
    #         wait.until(EC.presence_of_element_located(date_locator))
    #         # wait.until(EC.)
    #         _date = driver.find_element(*date_locator).text.encode('utf-8')
    #
    #         wait.until(EC.presence_of_element_located(price_locator))
    #         price_list = [float(x.text.split(' ')[0].encode('utf-8').replace('≈', '').replace(',', ''))
    #                       for x in driver.find_elements(*price_locator)]
    #         l.append((_date, min(price_list)))
    #
    #         wait.until(EC.presence_of_element_located(next_url_locator))
    #         url_ = driver.find_element(*next_url_locator).get_attribute("href")
    #
    #     print l
    #     # write_file(d)
    # except BaseException, e:
    #     print e
    #     # driver.close()
    #     # driver.quit()
    # finally:
    #     write_file(_begin_date, _src, _dst, l)


def init():
    pass
    # try:
    #     driver.get(r'http://www.airasia.com/cn/zh/home.page')
    #     # title_contains(u'亚洲')
    #     WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//title")))
    # except BaseException, e:
    #     print e


def get_lowest_price_multi(_begin_date, _src, _dst, _count):
    try:
        #init()

        l = []
        #pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        pool = multiprocessing.Pool(processes=3)
        for i in xrange(_count):
            l.append(pool.apply_async(get_lowest_price, (_begin_date, _src, _dst, i)))

        print "Started processes"
        pool.close()
        pool.join()
        print "Subprocess done."
        print l
    except BaseException, e:
        print e

# class MutiGetPrice(object):
#     def __init__(self):
#         pass
#         # self._date_locator = (By.XPATH, "//li[@class='active']//h3[@class='low-fare-date']")
#         # self._price_locator = (By.XPATH, "//div[@class='avail-fare-price']")
#         # self._next_url_locator = (By.XPATH, "//li[@class='not-active'][4]//a")
#         #
#         # # 警用图片加载
#         # chromeOptions = webdriver.ChromeOptions()
#         # prefs = {"profile.managed_default_content_settings.images": 2}
#         # chromeOptions.add_experimental_option("prefs", prefs)
#         # self._driver = webdriver.Chrome(chrome_options=chromeOptions)
#         # self._wait = WebDriverWait(self._driver, 5)
#
#     def get_lowest_price(self, msg):
#         print 'receive', msg
#         #return _day_delta
#
#     def run(self, _begin_date, _src, _dst, _count):
#         pass
#         # self._driver.get(r'http://www.airasia.com/cn/zh/home.page')
#         # self._wait.until(EC.presence_of_element_located((By.XPATH, "//title")))



if __name__ == '__main__':
    # 香港：HKG
    # 曼谷廊曼：DMK
    # 深圳：SZX
    get_lowest_price_multi('2017-06-15', 'SZX', 'DMK', 10)



    #d.run('2017-06-15', 'SZX', 'DMK', 10)
    # get_lowest_price_multi('2017-06-15', 'SZX', 'DMK', 365)
    # driver.close()
    # driver.quit()