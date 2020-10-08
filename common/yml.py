# @Time : 2020/10/6 13:54
# @Author : LeeWJ
# @Function  : yml文件读取
# @Version  : 1.0

from common import logger
import yaml

class Yml:
    """
        读取Yml文件
    """

    # 构造函数打开yml
    def __init__(self, path, t='r', coding='utf8'):
        """
        初始化实例，打开一个yml文件
        :param path: txt的路径
        :param t: 打开文件的方式，r:只读(默认)；w:只写；rw:可读写
        :param coding: 打开文件的编码，默认utf8
        """
        with open(path,t,encoding=coding) as self.f:
            self.data = self.f.read()

    def read_yml(self):
        return yaml.load(self.data,Loader=yaml.FullLoader)