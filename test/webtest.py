# @Time : 2020.7.4
# @Author : LeeWJ
# @Function  :  web UI自动化测试流程用
# @Version  : 1.0

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time


#显式等待，单个元素
def wait_element(by_, element_):
    element = WebDriverWait(driver, timeout=10).until(
        ec.presence_of_element_located((by_, element_))
    )
    return element

#显式等待，多个元素
def wait_elements(by_, element_):
    element = WebDriverWait(driver, timeout=10).until(
        ec.presence_of_all_elements_located((by_, element_))
    )
    return element

#手工添加cookie
def add_cookie_str(cookie_str):
    for item in cookie_str.split(';'):  # cookie字符串转list
        cookie = dict()
        itemname = item.split('=')[0]
        itemvalue = item.split('=')[1]
        cookie.update({
            'name': itemname.strip(' '),  #去除首尾空格（复制浏览器的会在最开头有空格）
            'value': itemvalue.strip(' '),
            "domain": "",
            "expires": "",
            'path': '/',
            'httpOnly': False,
            'HostOnly': False,
            'secure': False,
        })
        driver.add_cookie(cookie)
    return 1

def go(driver):
    #driver.implicitly_wait(10)
    #目标网址
    driver.get('https://')
    driver.delete_all_cookies()
    #手工添加cookie
    add_cookie_str('')

    #write something here ...

#调试webUI自动化专用
if __name__ =='__main__':
    driver = webdriver.Chrome()
    go(driver)