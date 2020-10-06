# @Time : 2020.7.17
# @Author : LeeWJ
# @Function  :  自动化架构体系，数据驱动运行入口
# @Version  : 2.1

import json, traceback, requests,jsonpath,time

from common import logger#, Encrypt
from inter.commonKeys import sysKey
from common.mysql import Mysql


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
        try:
            if proxies:
                proxies = eval(proxies)
        except Exception as e:
            proxies = None
            logger.error(f'代理设置失败：{str(e)}')
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
        try:
            if proxies:
                proxies = eval(proxies)
        except Exception as e:
            proxies = None
            logger.error(f'代理设置失败：{str(e)}')
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

        if value is None or value == '':
             value = ''
        #对value进行MD5加密
        import hashlib
        value = hashlib.md5(value.encode(encoding='UTF-8')).hexdigest()
        # 保存键值对到关联字典
        sysKey.relations[paramname] = value

        self.__write_excel(True, value)
        return True

    def sleep(self, t):
        """
        固定等待
        :param t：延时时间，单位s
        :return: 返回成功失败
        """
        try:
            time.sleep(int(t))
            self.__write_excel(True, "等待")
            return True
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

    def ts(self,length='',paramname=''):
        """
        创建当前时间戳
        :param length: 时间戳长度，不传此字段时或传10时，默认10位，length为13或其他值时，为13位
        :param paramname: 保存后参数的名字
        :return: 成功失败
        """

        #默认该参数名为ts
        if paramname is None or paramname == '':
            paramname = 'ts'

        #时间戳10位的情况
        if length is None or length == '' or length == 10 or length == '10':
            timestamp = str(time.time())[:10]
        #时间戳13位的情况
        else:
            timestamp = str(time.time())[:10] + '000'

        # 保存键值对到关联字典
        sysKey.relations[paramname] = timestamp

        self.__write_excel(True, timestamp)
        return True



    def randomcreate(self, type,length,paramname):
        """
        随机数生成器
        :param type: 随机数生成类型，可选：1：随机大小写英文数字、2：随机数字 、3:随机大写英文 、4：随机小写英文、
                        5：随机大小写英文、6：随机大写英文+数字、7：随机小写英文+数字
        :param length: 生成的长度
        :param paramname：保存为全局变量的变量名
        :return: 成功失败
        """
        #默认赋值
        type = '1' if not type else type
        length = '7' if not length else length
        paramname = 'ran_str' if not paramname else paramname
        try:
            length = int(length)
        except Exception as e:
            logger.error(str(e))
            self.__write_excel(False, traceback.format_exc())
            return False
        import random,string
        #随机大小写英文数字
        if type == '1':
            ran_str = ''.join(random.sample(string.ascii_letters + string.digits, length))
        #随机数字，这里通过列表推导式生成不然数字过长会报错
        elif type == '2':
            ran_str = ''.join([''.join(random.sample(string.digits , 1)) for i in range(length)])
        #随机大写英文
        elif type == '3':
            ran_str = ''.join(random.sample(string.ascii_letters, length)).upper()
        #随机小写英文
        elif type == '4':
            ran_str = ''.join(random.sample(string.ascii_letters, length)).lower()
        #随机大小写英文
        elif type == '5':
            ran_str = ''.join(random.sample(string.ascii_letters, length))
        #随机大写英文+数字
        elif type == '6':
            ran_str = ''.join(random.sample(string.ascii_letters + string.digits, length)).upper()
        #随机小写英文+数字
        elif type == '7':
            ran_str = ''.join(random.sample(string.ascii_letters + string.digits, length)).lower()

        #如果都不匹配，就随机大小写英文数字
        else:
            ran_str = ''.join(random.sample(string.ascii_letters + string.digits, length))

        # 保存键值对到关联字典
        sysKey.relations[paramname] = ran_str
        self.__write_excel(True, ran_str)
        return True


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

    def assertmysql(self,sql,dictv):
        '''
        与mysql数据库指定值作比较
        sql:要查询的sql语句
        dictv:断言条件，形式:{n1:'value1',n2:'value2'}  例子：{2:'Jack',3:23}，（说明要比较查询结果的某一行是否同时存在第二列为Jack及第三列为23）
        '''
        # 实现关联
        dictv = self.__get__relations(dictv)

        if sql.upper().startswith('SELECT'):
            #回写excel的数据
            writeexcel = ''
            #返回查询结果，mysqlcheck是一个元组，里面又包含了每一行的查询结果（每一行一个元组），形如((1,"Jack",23),(2,"Tom",16))
            mysqlcheck = Mysql().mysqlexec(sql)
            if 'error!!!' in mysqlcheck:
                self.__write_excel(False, mysqlcheck)
                logger.error('sql查询出错')
                return False
            #字符串转字典
            #dictv = eval(f'{{{dictv}}}')
            dictv = eval(dictv)
            logger.info(mysqlcheck)
            try:
                # 遍历每一行
                for i in mysqlcheck:
                    flag = True
                    # 遍历行中的每一列
                    for j in range(len(i)):
                        value = i[j]
                        #先判断dict的键存不存在
                        if j + 1 not in dictv:
                            continue
                        #如果某一值不符合断言就pass掉
                        if dictv[j + 1] != value:
                            flag = False
                            break
                    if flag:
                        #print(i)
                        writeexcel += str(i)
                        #break
                if writeexcel:
                    self.__write_excel(True, writeexcel)
                    return True
                else:
                    self.__write_excel(False, writeexcel)
                    return False
            except Exception as e:
                logger.error(f'比较sql时发生了错误：{str(e)}')
                self.__write_excel(False, traceback.format_exc())
                return False
        else:
            logger.error('不是以SELECT开头的sql语句，无法进行比较')
            self.__write_excel(False,'不是以SELECT开头的sql语句，无法进行比较')
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

        #获取json数据时可能会获取到int类型的数据，故需转换为str
        if isinstance(params,int):
            params = str(params)

        for key in sysKey.relations.keys():
            params = params.replace(f'${{{key}}}', str(sysKey.relations[key]))
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

