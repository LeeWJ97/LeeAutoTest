# @Time : 2020.7.17
# @Author : LeeWJ
# @Function  :  自动化架构体系，数据驱动运行入口
# @Version  : 2.1

import json, traceback, requests,jsonpath

from common import logger#, Encrypt
from inter.commonKeys import sysKey


class HTTP:
    def __init__(self, writer):
        # 创建session管理
        self.session = requests.session()
        # 设置请求默认的头
        self.session.headers.update({'content-type':'application/x-www-form-urlencoded'})
        self.session.headers.update({'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'})
        # 项目接口基本地址
        self.url = ""
        # 保存请求结果
        self.result = None
        # 保存json解析后的字典
        self.jsonres = None
        # 写入结果的对象
        self.writer = writer
        # 记录关键字运行时，写入excel的行
        self.row = 0

    def seturl(self, url):
        """
        设置项目接口基本地址
        :param url: 项目的基本地址
        :return: 成功失败
        """
        # 对传入参数的处理
        if url is None or url == '':
            url = ''

        self.url = url
        self.__write_excel(True, self.url)
        return True

    def get(self, path, params,proxies=None):
        """
        以data字典形式传键值对参数
        :param path: 接口地址
        :param params: 参数字典
        :return: 成功失败
        """

        #如果代理被设置，则转换为json
        if proxies:
            proxies = eval(proxies)
        # 对传入参数的处理
        if params is None or params == '':
            params = None

        # 对path进行处理
        if path is None or path == '':
            # 接口地址不应该为空
            self.__write_excel(False, "接口地址不应该为空")
            return False
        # 实现关联
        params = self.__get__relations(params)

        # 如果传非绝对路径的地址，就拼上基础地址
        if not path.startswith("http"):
            path = f'{self.url}/{path}'

        # 处理url连接失败的情况
        try:
            self.result = self.session.get(f'{path}?{params}',proxies=proxies,verify=False)
        except Exception as e:
            self.result = None

        try:
            # 如果返回的是json字符串，就处理为字典
            resulttext = self.result.text
            resulttext = resulttext[resulttext.find('{'):resulttext.rfind('}') + 1]
            self.jsonres = json.loads(resulttext)
            self.__write_excel(True, self.jsonres)
        except Exception as e:
            logger.exception(e)
            self.jsonres = None
            if self.result is None:
                self.__write_excel(False, None)
            else:
                self.__write_excel(True, self.result.text)

        return True

    def post(self, path, params,proxies=None):
        """
        以data字典形式传键值对参数
        :param path: 接口地址
        :param params: 参数字典
        :return: 成功失败
        """

        #如果代理被设置，则转换为json
        if proxies:
            proxies = eval(proxies)
        # 对传入参数的处理
        if params is None or params == '':
            params = None

        # 对path进行处理
        if path is None or path == '':
            # 接口地址不应该为空
            self.__write_excel(False, "接口地址不应该为空")
            return False
        # 实现关联
        params = self.__get__relations(params)

        ############################注意加密
#        params = self.__use_encrypt(params)

        params = self.__get_data(params)

        # 如果传非绝对路径的地址，就拼上基础地址
        if not path.startswith("http"):
            path = f'{self.url}/{path}'

        # 处理url连接失败的情况
        try:
            self.result = self.session.post(path, data=params,proxies=proxies,verify=False)
        except Exception as e:
            self.result = None

        try:
            # 如果返回的是json字符串，就处理为字典
            resulttext = self.result.text
            resulttext = resulttext[resulttext.find('{'):resulttext.rfind('}') + 1]
            self.jsonres = json.loads(resulttext)
            self.__write_excel(True, self.jsonres)
            print(str(self.jsonres))
        except Exception as e:
            logger.exception(e)
            print(self.result.text)
            print(str(traceback.format_exc()))
            self.jsonres = None
            if self.result is None:
                self.__write_excel(False, None)
            else:
                self.__write_excel(True, self.result.text)

        return True

    def addheader(self, key, value):
        """
        往请求头里面添加一个键值对
        :param key: 头的键
        :param value: 头的值
        :return: 成功失败
        """
        value = self.__get__relations(value)
        self.session.headers[key] = value
        self.__write_excel(True, self.session.headers)
        return True

    def removeheader(self, key):
        """
        从请求头删除一个键值对
        :param key: 需要删除的键
        :return: 成功失败
        """
        try:
            self.session.headers.pop(key)
        except Exception as e:
            pass

        self.__write_excel(True, self.session.headers)
        return True

    def assertequals(self, key, value):
        """
        断言json结果里面某个键的值和value相等
        :param key: json的键
        :param value: 期望值
        :return: 是否相等
        """
        # 如果请求返回不是json，就直接return
        if self.jsonres is None:
            self.__write_excel(False, None)
            print(self.jsonres)
            return False

        value = self.__get__relations(value)

        try:
            actual = str(jsonpath.jsonpath(self.jsonres, key)[0])
            if actual == str(value):
                self.__write_excel(True, actual)
                return True
            else:
                self.__write_excel(False, actual)
                print(f"预期结果：{str(value)}")
                print(f"实际结果：{str(actual)}")
                return False
        except Exception as e:
            # 处理键不存在的情况
            self.__write_excel(False, traceback.format_exc())
            print(str(traceback.format_exc()))
            return False

    def savejson(self, jsonkey, paramname):
        """
        从jsonres里面保存某个键的值，用来关联
        :param jsonkey: 需要保存的json的键
        :param paramname: 保存后参数的名字
        :return: 成功失败
        """
        # 去jsonres里面取值
        try:
            value = str(jsonpath.jsonpath(self.jsonres, jsonkey)[0])
        except Exception as e:
            value = None
        # 保存键值对到关联字典
        sysKey.relations[paramname] = value

        self.__write_excel(True, sysKey.relations)
        return True

    def md5(self, value, paramname):
        """
        md5指定值并保存，用来关联
        :param value: 要MD5的值
        :param paramname: 保存后参数的名字
        :return: 成功失败
        """
        #对value进行MD5加密
        import hashlib
        value = hashlib.md5(value.encode(encoding='UTF-8')).hexdigest()
        # 保存键值对到关联字典
        sysKey.relations[paramname] = value

        self.__write_excel(True, value)
        return True

    def assertequaljson(self, jsonp):
        """
        断言json结果里多个键值对相等
        :param jsonp: 传入你需要比较的多个键值对的json字符串
        :return: 是否相等
        """
        # 如果请求返回不是json，就直接return
        if self.jsonres is None:
            self.__write_excel(False, None)
            return False

        try:
            # 传入的参数不是json，传参错误
            jsonp = eval(jsonp)
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

        try:
            # 处理键不存在的情况
            for key in jsonp.keys():
                # 只要有一个键值对不相等，就不相等
                value = str(jsonpath.jsonpath(self.jsonres, key)[0])
                if not value == str(jsonp[key]):
                    self.__write_excel(False, self.jsonres)
                    return False
            # 所有键值对都相等，才返回True
            self.__write_excel(True, self.jsonres)
            return True
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

    def assertcontains(self, value):
        """
        断言返回结果的字符串包含value
        :param value: 被包含的字符串
        :return: 是否包含
        """
        try:
            # 如果返回结果为空，就报错
            result = str(self.result.text)
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

        value = self.__get__relations(value)

        if result.__contains__(str(value)):
            self.__write_excel(True, self.result.text)
            return True
        else:
            self.__write_excel(False, self.result.text)
            return False

    def __get_data(self, params):
        """
        url参数转字典
        :param params: 需要转字典的参数
        :return: 转换后的字典
        """
        if params is None:
            return None

        # 定义一个字典，用来保存转换后的参数
        param = {}
        p1 = params.split('&')
        for keyvalue in p1:
            index = keyvalue.find('=')
            if index >= 0:
                key = keyvalue[0:index]
                value = keyvalue[index + 1:]
                param[key] = value
            else:
                param[keyvalue] = ''

        return param

    def __get__relations(self, params):
        """
        使用关联结果
        :param params: 需要关联的参数
        :return: 关联后的字符串
        """
        if params is None:
            return None

        for key in sysKey.relations.keys():
            params = params.replace('{' + key + '}', str(sysKey.relations[key]))
        return params

    def __write_excel(self, status, msg):
        """
        写入关键字运行结果
        :param status: 运行的状态
        :param msg: 实际运行结果
        :return: 无
        """
        if status is True:
            self.writer.write(self.row, 7, "PASS", 3)
        else:
            self.writer.write(self.row, 7, "FAIL", 2)

        # 有时候实际结果过长，由于excel自身限制，只能保存前32767个字符
        msg = str(msg)
        if len(msg) > 32767:
            msg = msg[0:32767]

        self.writer.write(self.row, 8, str(msg))

    # def __use_encrypt(self,params):
    #     """
    #     替换加密后的字符串
    #     :param s: 需要加密的字符串
    #     :return: 加密后的字符串
    #     """
    #     # 递归的思维，当字符串里面既有[,又有]的时候
    #     # 反复的执行如下替换
    #     if params is None:
    #         return ''
    #     elif params.find('[') >= 0 and params.find(']') >= 0:
    #         en_s = params[params.find('[') + 1:params.find(']')]
    #         en_s1 = Encrypt.encrypt(en_s)
    #         params = params.replace('[' + en_s + ']', en_s1)
    #         return self.__use_encrypt(params)
    #     else:
    #         return params

