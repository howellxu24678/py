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
def is_bookable(book_locator):
    try:
        wait = WebDriverWait(driver, 2, 0.5)
        wait.until(EC.presence_of_element_located(book_locator))
        return True
    except BaseException,e:
        print e
        return False

def book(book_href):
    try:
        wait = WebDriverWait(driver, 3, 0.5)
        driver.get(book_href)
        #默认选取可预约的最早的那个时间段（第一个）
        time_locator = (By.XPATH, "//div[@class='fn-left yy-time']/ul[@class='fn-clear']/li[1]")
        wait.until(EC.presence_of_element_located(time_locator))
        driver.find_element(*time_locator).click()

        #勾选医院预约规则
        input_locator = (By.XPATH, "//div[@class='order-con']/div[@class='block p10']//input")
        wait.until(EC.presence_of_element_located(input_locator))
        inp = driver.find_element(*input_locator)
        if not inp.is_selected():
            inp.click()

        #勾选现场支付 //div[@class='pay-list']/input[@name='pay_online' and @type='radio' and @value='0']/following-sibling::label
        pay_locator = (By.XPATH, "//div[@class='pay-list']/input[@name='pay_online' and @type='radio' and @value='0']/following-sibling::label")
        wait.until(EC.presence_of_element_located(pay_locator))
        pay = driver.find_element(*pay_locator)
        if not pay.is_selected():
            pay.click()

        #不勾选领取保险
        cb_locator = (By.XPATH, "//div[@class='order-con fn-clear']//input[@type='checkbox']")
        wait.until(EC.presence_of_element_located(cb_locator))
        cb = driver.find_element(*cb_locator)
        if cb.is_selected():
            cb.click()

        #处理验证码
        verifycode_img_locator = (By.XPATH, "//div[@class='fn-clear block tj-order']/div[@class='tjecode']/img")
        wait.until(EC.presence_of_element_located(verifycode_img_locator))
        verifycode_img_src = driver.find_element(*verifycode_img_locator).get_property("src")


        verifycode_input_locator = (By.XPATH, "//div[@class='tjecode']/input[@name='captcha']")
        wait.until(EC.presence_of_element_located(verifycode_input_locator))
        verifycode_input = driver.find_element(*verifycode_input_locator)
        verifycode_input.click()

        screenshot_filename = datetime.datetime.now().strftime("%H%M%S%f")[:-3] + ".jpg"
        path_screenshot = os.path.join(os.getcwd(), screenshot_filename)
        driver.save_screenshot(path_screenshot)


        return True
    except BaseException,e:
        print e
        return False


# ap:1上午，2下午
def autobook(link, ap):
    try:
        book_locator = (By.XPATH, "//li[@class='liClassData'][%d]/div[@class='yuyuebor']/a" % ap)
        driver.get(link)
        while(True):
            if not is_bookable(book_locator):
                driver.refresh()
                time.sleep(1)
            else:
                print "can book!"
                book_href = driver.find_element(*book_locator).get_property("href")
                print "book_href %s" % book_href
                #预约成功才退出循环
                if book(book_href):
                    break
                else:
                    #当进入了预定处理逻辑之后，网页的链接被改变了
                    driver.get(link)
    except BaseException,e:
        print e
    finally:
        pass
        #driver.close()

login("18719286683", "0730xujhao")
autobook("https://www.91160.com/doctors/index/docid-100214968.html", 2)


#driver.close()



# driver.get("https://www.91160.com/doctors/index/docid-100220574.html")
# # driver.get("https://www.91160.com/dep/show/depid-2161.html")
#
# # bt = driver.find_element_by_class_name("_tips_btn_green")
# # bt.click()
#
#
# driver.refresh()

