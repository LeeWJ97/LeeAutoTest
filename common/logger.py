# @Time : 2020.7.17
# @Author : LeeWJ
# @Function  :  日志打印模块，格式化打印日志到文件、控制台
# @Version  : 2.1

import logging,os
import time

from inter.commonKeys import sysKey
#指定日志文件存放路径及日志文件名


path = f'{sysKey.path}\\log\\'
logfile = f"AllLog_{str(sysKey.stamp2time(int(time.time()*1000))).replace('-','_').replace(':','_').replace(' ','_')}.log"
print(path)

#日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#判断日志文件存放路径是否存在，若不存在则自动创建相关文件夹
if not os.path.exists(path):
    os.mkdir(path)
c = logging.FileHandler(f'{path}\\{logfile}', mode='a', encoding='utf8')
logger = logging.getLogger('frame log')
logger.setLevel(logging.DEBUG)
c.setFormatter(formatter)
logger.addHandler(c)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# 打印debug级别日志
def debug(str):
    global logger
    try:
        logger.debug(str)
    except:
        return

# 打印info级别日志
def info(str):
    global logger
    try:
        logger.info(str)
    except:
        return

# 打印warn级别日志
def warn(str):
    global logger
    try:
        logger.warning(str)
    except:
        return

# 打印error级别日志，错误日志增加！！！高亮显示
def error(str):
    global logger
    try:
        logger.error(f'!!! {str}')
    except:
        return

# 打印异常日志，异常日志增加！！！高亮显示
def exception(e):
    global logger
    try:
        logger.exception(f'!!! {e}')
    except:
        return

# 调试
if __name__ == '__main__':
    debug('test debug')
    info('test info')
    warn('test warn')
    error('test error')
    exception('test exception')


