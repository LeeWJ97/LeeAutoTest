# @Time : 2020.7.17
# @Author : LeeWJ
# @Function  :  配置文件读取模块
# @Version  : 2.1

from common import logger
from common.txt import Txt

# 全局变量，用来存储配置
config = {}


def get_config(path):
    """
    读取配置文件,配置文件格式：#为注释，配置格式value=key
    :param path:配置文件路径
    :return:返回配置文件dict
    """
    global config
    # 重新获取时，先清空配置
    config.clear()
    txt = Txt(path)
    data = txt.read()

    for s in data:
        # 跳过注释
        if s.startswith('#'):
            continue

        if not s.find('=') > 0:
            logger.warn(f'配置文件格式错误，请检查：{str(s)}')
            continue

        try:
            key = s[0:s.find('=')]
            value = s[s.find('=') + 1:s.__len__()]
            config[key] = value
        except Exception as e:
            logger.warn(f'配置文件格式错误，请检查：{str(s)}')
            logger.exception(e)

    return config
