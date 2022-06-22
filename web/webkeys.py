# @Time : 2020.7.17
# @Author : LeeWJ
# @Function  :  web UI自动化模块
# @Version  : 2.1

import os
import re
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from inter.commonKeys import sysKey
import inter.commonKeys
from common import logger, config,xpathmap


class Web:
    """
    封装Web自动化函数
    """

    def __init__(self, writer):
        self.driver = None
        # 写入excel的对象
        self.writer = writer
        # 写入的行
        self.row = 0
        # 保存查找元素失败的异常
        self.e = None

    def openbrowser(self, br="gc",ex=""):
        """
        打开浏览器
        :param br: gc=谷歌浏览器(默认)；ff=火狐浏览器；ie=ie浏览器
        :param ex: 对应driver的路径，默认在项目的lib目录
        :return: 打开成功失败
        """
        try:
            if br is None or br == "gc" or br == "":
                # 使用用户文件加载缓存和配置chrome的安装路径
                # 创建一个chrome的配置项对象
                option = webdriver.ChromeOptions()
                # 获取用户文件路径
                userfile = os.environ["USERPROFILE"]

                if str(config.config.get('UIheadless')) == "True":
                    logger.info(f"Using Chrome --headless: {str(config.config.get('UIheadless'))}")
                    option.headless = True

                # 添加用户文件配置
                # 使用缓存，也使用了cookie
                #option.add_argument("--user-data-dir=%s\\AppData\\Local\\Google\\Chrome\\user data"
                #                    % userfile)
                # 配置chrome安装路径
                # option.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

                # 打开浏览器
                if ex == "":
                    ex = "./lib/conf/chromedriver.exe"

                self.driver = webdriver.Chrome(executable_path=ex,options=option)
                if str(config.config.get('UIheadless')) == "True":
                    self.driver.set_window_size(1920,1080)
                #self.driver.maximize_window()

            elif br == 'ff':
                if ex == "":
                    ex = "./lib/conf/geckodriver.exe"

                # 有cookie的，但是缓存不存在，所以加载还是比较慢
                # 使用cmd命令去创建一个用户文件
                # "C:\Program Files\Mozilla Firefox\firefox.exe" -p
                opt = webdriver.FirefoxOptions()
                opt.profile = rf'{os.environ["USERPROFILE"]}\AppData\Roaming\Mozilla\Firefox\Profiles\mytest.mytest'
                self.driver = webdriver.Firefox(executable_path=ex, firefox_options=opt)

            elif br == 'ie':
                if ex == "":
                    ex = "./lib/conf/IEDriverServer.exe"
                opt = webdriver.IeOptions()
                opt.profile = rf'{os.environ["USERPROFILE"]}\Local\Microsoft\Windows\INetCache'
                self.driver = webdriver.Ie(executable_path=ex, options=opt)

            # 添加隐式等待
            #self.driver.implicitly_wait(10)
            self.__write_excel(True, "Browser Open successfully")
            # self.driver.find_element_by_partial_link_text()
            # self.driver.get_screenshot_as_png()

            return True

        except Exception as e:
            logger.exception(str(traceback.format_exc()))
            self.__write_excel(False, traceback.format_exc())
            self.writer.save_close()
            exit(-1)

    def geturl(self, url):
        """
        打开网站
        :param url: 网址
        :return: 成功失败
        """
        if self.driver is None:
            self.__write_excel(False, "Browser not exist")
            return False
        try:
            self.driver.get(url)
            self.__write_excel(True, f"Open URL: {url} successfully")
            return True
        except Exception as e:
            logger.exception(str(traceback.format_exc()))
            self.__write_excel(False, f"Open URL: {url} failed")
            #logger.exception(e)
            return False

    def click(self, locator):
        """
        通过定位器找到元素点击
        :param locator: 定位器
        :return: 点击成功失败
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False
        try:
            ele.click()
            self.__write_excel(True, "Click successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def whiletryclick(self, locator,manyclick=True):
        """
        通过定位器找到元素while try点击
        :param locator: 定位器
        :return: 点击成功失败
        """
        time.sleep(0.8)
        trycount = 20
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False
        if str(manyclick).lower() != "false":
            manyclick = True
        else:
            manyclick = False
        while 1:
            try:
                #print('try')
                ele.click()
                if manyclick == True:
                    print(f'{manyclick} more click: {locator}')
                    locator = self.__xpath_map(locator)
                    for i in range(3):
                        try:
                            ele = self.driver.find_element_by_xpath(locator)
                            ele.click()
                            time.sleep(0.1)
                        except Exception as e:
                            print(f'Many click {locator}: {str(e)}')
                self.__write_excel(True, "click successfully")
                return True
            except Exception as e:
                if trycount <= 0:
                    screenshotfile = self.take_screenshot()
                    logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
                    self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
                    return False
                ele = self.__find_ele(locator)
                trycount-=1
                time.sleep(0.5)


    def clickhref(self, locator):
        """
        通过定位器找到a标签元素，然后获取到href连接，进行跳转，主要用于处理IE点击失败的情况
        :param locator: 定位器
        :return: 点击成功失败
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False

        try:
            href = ele.get_attribute('href')
            self.driver.get(href)
            self.__write_excel(True, "href click successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def get_attribute(self, locator,attributename,param='attr'):
        """
        通过定位器找到a标签元素，然后获取到href连接，进行跳转，主要用于处理IE点击失败的情况
        :param locator: 定位器
        :return: 点击成功失败
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False

        try:
            attr = ele.get_attribute(attributename)
            # 设置到关联字典
            sysKey.relations[param] = attr
            self.__write_excel(True, f"get attribute successfully: {attr}")
            return attr
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def wait_ele_can_find(self, locator,attr=None):
        """
        通过定位器找到a标签元素，然后获取到href连接，进行跳转，主要用于处理IE点击失败的情况
        :param locator: 定位器
        :return: 点击成功失败
        """
        trycount = 50
        if locator is None:
            self.__write_excel(False, f'{locator} cannot be None')
            return False
        while 1:
            try:
                ele = self.__find_ele(locator)
                if str(attr).strip(' '):
                    attrvalue = self.get_attribute(locator,attr)
                    if 'disabled' in attrvalue:
                        logger.error(f'disabled found: {locator} {attr} = {attrvalue}  {str(trycount)}')
                        raise Exception(f'disabled found: {locator} {attr} = {attrvalue}  {str(trycount)}')
                self.__write_excel(True, f"Get successfully")
                return True
            except Exception as e:
                if trycount <= 0:
                    screenshotfile = self.take_screenshot()
                    logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
                    self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
                    return False
                trycount -= 1
                time.sleep(0.5)

    def jsclick(self, locator):
        """
        通过js点击a标签，针对selenium点击不了的情况
        （点击a标签触发js事件的，JavaScript:void(0);）
        :param locator: 定位器
        :return: 点击成功/失败
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False

        try:
            self.driver.execute_script("$(arguments[0]).click()", ele)
            self.__write_excel(True, "js click succesfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def runjs(self, js):
        """
        执行自定义js
        :param locator: 定位器
        :return: 执行成功失败
        """
        try:
            time.sleep(1)
            self.driver.execute_script(js)
            self.__write_excel(True, f"js run successfully: {js}")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def getimg(self,locator,filename=""):
        """
        获取元素截图
        :param locator: 定位器
        :param filename: 截图后保存的名字
        :return: 截图是否成功
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False

        if filename == '':
            filename = 'ele_pic'

        try:
            #如果路径不存在，则自动创建
            if not os.path.exists('./lib/ele_pic/'):
                os.mkdir('./lib/ele_pic/')
            filename = f'./lib/ele_pic/{filename}.png'
            ele.screenshot(filename)
            self.__write_excel(True, f"take screenshot for {locator} successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def take_screenshot(self,filename=''):
        if not os.path.exists(f'{sysKey.path}\\log\\screenshot'):
            os.mkdir(f'{sysKey.path}\\log\\screenshot')
        if (str(filename).strip(' ') == '') or (filename is None):
            filename = str(sysKey.stamp2time(int(time.time()*1000))).replace('-','_').replace(':','_').replace(' ','_')
        fullfilename = f'{sysKey.path}\\log\\screenshot\\{filename}.png'
        self.driver.save_screenshot(fullfilename)
        return fullfilename

    def input(self, locator, text):
        """
        输入框输入文字
        :param locator: 定位器
        :param text: 需要输入的文本
        :return: 输入成功失败
        """
        time.sleep(2)
        text = str(text)
        ele = self.__find_ele(locator)

        if ele is None:
            self.__write_excel(False, self.e)
            return False

        # 如果输入的是操作键盘
        if str(text).startswith('Keys.'):
            text = eval(text)
        else:
            #replace random text
            if '{randomcreate}' in text:
                text = str(text).replace('{randomcreate}',inter.commonKeys.sysKey.randomcreate(1,10))
                logger.info(f'input replace random text: {text}')
        try:
            text = self.__get__relations(text)

            try:
                ele.send_keys(text)
            except:
                ele = self.__find_ele(locator)
                ele.send_keys(text)
            time.sleep(1.5)
            self.__write_excel(True, "Input successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def inputfile(self, locator, text):
        """
        input标签上传文件
        :param locator: 定位器
        :param text: 需要上传的文件
        :return: 输入成功失败
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False

        try:
            text = f'{sysKey.path}/lib/verify/{text}'
            ele.send_keys(text)
            self.__write_excel(True, "input file successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def sleep(self, t):
        """
        固定等待
        :param t: 时间，单位s
        :return: 返回成功失败
        """
        try:
            time.sleep(int(t))
            self.__write_excel(True, "Sleep")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def quit(self):
        """
        退出浏览器
        :return: 成功失败
        """
        try:
            self.driver.quit()
            self.__write_excel(True, "quit")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def gettext(self,locator,param="text"):
        """
        获取元素的文本，并保存为关联后参数名：param
        :param locator: 定位器
        :param param: 保存后的参数名
        :return: 获取成功失败
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False

        trycount = 20
        while 1:
            try:
                text = ele.text
                if ((text == "") or (text is None)) and trycount > 0:
                    trycount-=1
                    ele = self.__find_ele(locator)
                    time.sleep(0.5)
                    continue
                # 设置到关联字典
                sysKey.relations[param] = text
                self.__write_excel(True, f"get text successfully: {text}")
                return True
            except Exception as e:
                screenshotfile = self.take_screenshot()
                logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
                self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
                return False

    def assertcontains(self, expectv,actualv):
        """
        web断言关键字，断言实际结果包含预期结果
        :param expectv: 预期结果
        :param actualv: 实际结果
        :return: 是否包含
        """

        # 关联
        actualv = self.__get__relations(actualv)
        expectv = self.__get__relations(expectv)

        if actualv.__contains__(str(expectv)):
            self.__write_excel(True, actualv)
            return True
        else:
            screenshotfile = self.take_screenshot()
            logger.error(f'{str(actualv)}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(actualv)}   | Screenshot: {str(screenshotfile)}')
            #self.__write_excel(False, actualv)
            return False

    def assertHTMLcontains(self, expectv):
        """
        web断言关键字，断言实际结果包含预期结果
        :param expectv: 预期结果
        :param actualv: 实际结果
        :return: 是否包含
        """
        trycount = 250
        while 1:
            page_source = self.driver.page_source


            if page_source.__contains__(str(expectv)):
                self.__write_excel(True, str(expectv))
                return True
            else:
                trycount-=1
                logger.info(f"Finding {expectv} if in page... {str(trycount)}")
                time.sleep(0.2)
                if trycount<=0:
                    screenshotfile = self.take_screenshot()
                    logger.error(f"No contain | Screenshot:  {str(screenshotfile)}")
                    self.__write_excel(False, f"No contain | Screenshot:  {str(screenshotfile)}")
                    return False

    def switchwindow(self,index=''):
        """
        窗口切换，切换到第index个窗口
        :param index: 窗口的下标
        :return: 切换是否成功
        """
        # 获取到所有窗口的handle列表
        if index == "" :
            index = 0

        try:
            handles = self.driver.window_handles
            self.driver.switch_to.window(handles[int(index)])
            self.__write_excel(True, "Switch window successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def intoiframe(self,locator):
        """
        进入locator指定的iframe
        :param locator: 定位iframe的定位器
        :return: 是否进入成功
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False

        try:
            # 进入iframe
            self.driver.switch_to.frame(ele)
            self.__write_excel(True, "enter successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def outiframe(self):
        """
        退出iframe
        :return: 是否退出成功
        """
        try:
            # 退出到最外面的HTML
            self.driver.switch_to.default_content()
            self.__write_excel(True, "out of iframe successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def movetoele(self,locator):
        """
        鼠标悬停
        :param locator: 定位iframe的定位器
        :return: 是否成功
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False
        try:
            ActionChains(self.driver).move_to_element(ele).perform()
            self.__write_excel(True, f"move to {locator} successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def dubbleclick(self,locator):
        """
        鼠标左键双击
        :param locator: 定位iframe的定位器
        :return: 是否成功
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False
        try:
            ActionChains(self.driver).double_click(ele).perform()
            self.__write_excel(True, "doubleclick successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def rightclick(self,locator):
        """
        鼠标右键单击
        :param locator: 定位iframe的定位器
        :return: 是否成功
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False
        try:
            ActionChains(self.driver).context_click(ele).perform()
            self.__write_excel(True, "right click successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def dragdrop(self,srclocator,dstlocator):
        """
        鼠标拖拽源元素到目标元素
        :param locator: 定位iframe的定位器
        :return: 是否成功
        """
        srcele = self.__find_ele(srclocator)
        dstele = self.__find_ele(dstlocator)
        if srcele is None or dstele is None:
            self.__write_excel(False, self.e)
            return False
        try:
            ActionChains(self.driver).drag_and_drop(srcele,dstele).perform()
            self.__write_excel(True, "drag and drop successfully")
            return True
        except Exception as e:
            screenshotfile = self.take_screenshot()
            logger.exception(f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            self.__write_excel(False, f'{str(traceback.format_exc())}   | Screenshot: {str(screenshotfile)}')
            return False

    def __get__relations(self, params):
        """
        使用关联结果
        :param params: 需要关联的参数
        :return: 关联后的字符串
        """
        if params is None:
            return None
        else:
            params = str(params)

        for key in sysKey.relations.keys():
            params = params.replace(f'${{{key}}}', str(sysKey.relations[key]))
        return params

    def __xpath_map(self,locator):
        if locator.startswith('#'):
            locator = xpathmap.XpathMap.read_xpath(locator[1:])
            return locator
        else:
            return locator

    def __find_ele(self, locator):
        """
        通过定位器找到元素
        :param locator: 默认xpath
        :return: 返回找到的元素
        """
        count = 40
        while 1:
            try:
                # find xpathmap
                locator = self.__xpath_map(locator)
                if locator is None:
                    print(f'{locator} is None, break')
                    break

                # 以%{开头，说明需要find_elements (xpath)
                if locator.startswith('%{'):
                    try:
                        # 获取索引值
                        i = locator[locator.find('{') + 1:locator.find('}')]
                        i = int(i)
                        locator = locator[locator.find('}') + 1:]
                        ele = self.__find_eles(locator, i)
                    except Exception as e:
                        self.e = traceback.format_exc()
                        logger.error(str(e))
                        return None
                elif locator.startswith("xpath="):
                    locator = locator[locator.find('=') + 1:]
                    ele = self.driver.find_element_by_xpath(locator)
                elif locator.startswith("id="):
                    locator = locator[locator.find('=') + 1:]
                    ele = self.driver.find_element_by_id(locator)
                elif locator.startswith("tagname="):
                    locator = locator[locator.find('=') + 1:]
                    ele = self.driver.find_element_by_tag_name(locator)
                elif locator.startswith("name="):
                    locator = locator[locator.find('=') + 1:]
                    ele = self.driver.find_element_by_name(locator)
                elif locator.startswith("linktext="):
                    locator = locator[locator.find('=') + 1:]
                    ele = self.driver.find_element_by_link_text(locator)
                elif locator.startswith("css="):
                    locator = locator[locator.find('=') + 1:]
                    ele = self.driver.find_element_by_css_selector(locator)
                elif locator.startswith("class="):
                    locator = locator[locator.find('=') + 1:]
                    ele = self.driver.find_element_by_class_name(locator)
                elif locator.startswith("partial="):
                    locator = locator[locator.find('=') + 1:]
                    ele = self.driver.find_element_by_partial_link_text(locator)
                else:
                    ele = self.driver.find_element_by_xpath(locator)
                    if str(config.config.get('UIheadless')) != "True":
                        self.driver.execute_script("arguments[0].setAttribute('style',arguments[1]);",
                                          ele, "border:4px solid yellow;")
                    # if ele.is_displayed() == False:
                    #     logger.info(f"{locator} is not displayed")
                    #     raise f"{locator} is not displayed"

                return ele

            except Exception as e:
                count -= 1
                time.sleep(0.5)
                logger.info(f'{count}:Trying to find ele:{locator}')
                if not count:
                    self.e = traceback.format_exc()
                    return None

    def __find_eles(self, locator,i):
        """
        通过定位器找到多个元素  xpath
        :param locator: xpath
        :return: 返回找到的元素ele
        :i：数组下标
        """
        count = 40
        while 1:
            try:
                #xpath定位
                #print(locator)
                i = int(i)
                #print(i)
                ele = self.driver.find_elements_by_xpath(locator)[i]
                #print(ele)
                return ele

            except Exception as e:
                count -= 1
                time.sleep(0.5)
                logger.info(f'{count}:Trying to find eles:{locator}')
                if not count:
                    self.e = traceback.format_exc()
                    return None


    def __write_excel(self, status, msg):
        """
        写入关键字运行结果
        :param status: 运行的状态
        :param msg: 实际运行结果
        """
        if status is True:
            self.writer.write(self.row, 7, "PASS", 3)
        else:
            self.writer.write(self.row, 7, "FAIL", 2)

        # 有时候实际结果过长，受excel限制只保存32767个字符
        msg = str(msg)
        if len(msg) > 32767:
            msg = msg[0:32767]

        self.writer.write(self.row, 8, str(msg))
