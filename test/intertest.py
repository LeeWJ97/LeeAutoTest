# @Time : 2020.7.21
# @Author : LeeWJ
# @Function  :  requests模块常用功能测试流程用
# @Version  : 1.1
import requests
from common import logger

class httpclass:
    #注：cookies请放在headers里
    def __init__(self,method,url,payload='',headers='',timeout=5,proxies=None):
        self.method = method
        self.url = url
        self.payload = payload
        self.headers = headers
        self.timeout = timeout
        self.proxies = proxies
        #payload = payload.encode('utf-8')

    def send(self):
        try:
            if self.method == 'get':
                self.res_data = requests.get(url=self.url, data=self.payload, headers=self.headers, timeout=self.timeout,proxies=self.proxies,verify=False)
            elif self.method == 'post':
                self.res_data = requests.post(url=self.url, data=self.payload, headers=self.headers, timeout=self.timeout,proxies=self.proxies,verify=False)
            elif self.method == 'put':
                self.res_data = requests.put(url=self.url, data=self.payload, headers=self.headers, timeout=self.timeout,proxies=self.proxies,verify=False)
            elif self.method == 'delete':
                self.res_data = requests.delete(url=self.url, data=self.payload, headers=self.headers, timeout=self.timeout,proxies=self.proxies,verify=False)
            elif self.method == 'options':
                self.res_data = requests.options(url=self.url, data=self.payload, headers=self.headers, timeout=self.timeout,proxies=self.proxies,verify=False)
            else:
                logger.error(f"ERROR:无效的方法，当前版本仅支持get\post\put\delete\options")
                return 0
            return 1
        except Exception as e:
            logger.error(f"send函数出现ERROR:{e}")
            return 0

    # 返回值的编码
    #类型：str
    def res_encoding(self):
        return self.res_data.encoding

    # 返回值的返回体文本
    # 类型：str
    def res_text(self):
        return self.res_data.text

    # 返回值的返回体，以字节形式（二进制）返回
    # 类型：bytes
    def res_content(self):
        return self.res_data.content

    # 返回值的返回头
    # 类型：<class 'requests.structures.CaseInsensitiveDict'>
    def res_headers(self):
        return self.res_data.headers

    # 返回值的状态码
    # 类型：int
    def res_status_code(self):
        return self.res_data.status_code

    # 返回原始响应体object，也就是 urllib 的 response 对象，使用 r.raw.read()  （少用）
    # 类型：<class 'urllib3.response.HTTPResponse'>
    def res_raw(self):
        return self.res_data.raw

    # 返回True或False，查看ok布尔值便可以知道是否请求成功
    # 类型：bool
    def res_ok(self):
        return self.res_data.ok

    # 返回json的响应体（Requests中内置的JSON解码器，以json形式返回,前提返回的内容确保是json格式的，不然解析出错会抛异常）
    #类型：dict字典
    def res_json(self):
        try:
            return self.res_data.json()
        except Exception as e:
            logger.error(f"JSONERROR:{e}")
            return 0

    # 失败请求(非200响应)抛出异常，正常时返回None （因状态码非200时直接抛出异常，故较少用，一般用res_status_code作判断）
    # 类型：当状态码为200时：<class 'NoneType'>；非200时则抛出异常终止程序
    def res_raise_for_status(self):
        return self.res_data.raise_for_status()

#requests测试
if __name__ == '__main__' :
    while 1:
        import json

        while 1:
            method = input("请输入方法(get/post/put/delete/options):")
            if method == "get" or method == "post"  or method == "put" or method == "delete" or method == "options":
                break
            else:
                print("method输入错误，必须为get/post/put/delete/options任一")

        while 1:
            url = input("请输入完整url：")
            if "http://" in url.lower() or "https://" in url.lower() :
                break
            else:
                print(f"您肯定输错了url，您输入的url中连http://或https://都没有（您输入的url是：{url})")

        while 1:
            headers = input('请输入headers（str，内部会自动转字典，例子：{"Content-Type":"application/json"}）：')
            if headers == "":
                headers = "{}"
            try:
                headers = eval(headers)
                break
            except Exception as e:
                print(f"headers json转换为dict失败，请重新输入headers：{e}")

        payload = input("请输入payload（str）：")

        while 1:
            try:
                timeout = input('请输入请求超时终止秒数（int）： ')
                timeout = int(timeout)
                break
            except ValueError:
                print('输错了，请输入一个int，例如3')

        while 1:
            proxies = input('请输入代理服务器，不输入则不需要（str，内部会自动转字典，例子：{"http":"127.0.0.1:6666","https":"127.0.0.1:6666"}）：')
            if proxies == "":
                proxies = None
            try:
                proxies = eval(proxies)
                break
            except Exception as e:
                print(f"proxies json转换为dict失败，请重新输入proxies：{e}")


        g = httpclass(method,url,payload,headers,timeout,proxies)
        if g.send() == 1 :
            msgheader = g.res_headers()
            msg = g.res_text()
            msgcode = g.res_status_code()
            print(msgheader)
            print(msg)
            print(f"状态码:{msgcode}")
        else:
            print("error\n\n")