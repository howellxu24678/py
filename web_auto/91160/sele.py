# -*- coding: utf-8 -*-
__author__ = 'xujh'

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time

driver = webdriver.Chrome()
#driver.implicitly_wait(10)



#根据用户名密码自动登录
def login(username, password):
    try:
        wait = WebDriverWait(driver, 5, 0.5)

        driver.get("https://user.91160.com/login.html")

        username_locator = (By.NAME, "username")
        wait.until(EC.presence_of_element_located(username_locator))
        driver.find_element(*username_locator).send_keys(username)

        password_locator = (By.NAME, "password")
        wait.until(EC.presence_of_element_located(password_locator))
        driver.find_element(*password_locator).send_keys(password)

        checkbox_locator = (By.CLASS_NAME, "check-box")
        wait.until(EC.presence_of_element_located(checkbox_locator))
        driver.find_element(*checkbox_locator).click()

        login_locator = (By.NAME, "loginUser")
        wait.until(EC.presence_of_element_located(login_locator))
        driver.find_element(*login_locator).click()
    except BaseException,e:
        print e
        #logger.exception(e)

#检查是否可以预约，传入医生的链接
def is_bookable(ap):
    try:
        wait = WebDriverWait(driver, 2, 0.5)

        book_locator = (By.XPATH, "//li[@class='liClassData'][%d]/div[@class='yuyuebor']/a" % ap)
        wait.until(EC.presence_of_element_located(book_locator))
        driver.find_element(*book_locator)
        #get_property("href")

        return True
    except BaseException,e:
        print e
        return False


# ap:1上午，2下午
def autobook(link, ap):
    driver.get(link)
    while(True):
        if not is_bookable(ap):
            time.sleep(1)
            driver.refresh()
        else:
            print "can book!"
            break




login("18719286683", "0730xujhao")
autobook("https://www.91160.com/doctors/index/docid-22611.html", 1)


#driver.close()



# driver.get("https://www.91160.com/doctors/index/docid-100220574.html")
# # driver.get("https://www.91160.com/dep/show/depid-2161.html")
#
# # bt = driver.find_element_by_class_name("_tips_btn_green")
# # bt.click()
#
#
# driver.refresh()

