from datetime import datetime
import time
import traceback




class sysKey:
    """
    系统关键字库，公共变量库
    """
    # 类变量，保存全局关联参数
    relations = {}
    # 项目绝对路径
    path = ""

    @staticmethod
    def randomcreate(type,length):
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
        try:
            length = int(length)
        except Exception as e:
            print(str(e))
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

        return ran_str

    @staticmethod
    # 时间转时间戳
    def time2stamp(timestr):
        try:
            datetime_obj = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")
            timestamp = int(
                time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)
        except Exception as e:
            print(e)
            return False
        return timestamp

    @staticmethod
    # 时间戳转时间
    def stamp2time(timestamp):
        try:
            k = len(str(timestamp)) - 10
            timestamp = datetime.fromtimestamp(timestamp / (1 * 10 ** k))
            timestr = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
            return timestr[:-3]
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    #调试
    print(sysKey.stamp2time(int(time.time()*1000)))