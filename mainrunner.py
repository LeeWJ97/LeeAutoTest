# @Time : 2020.7.17
# @Author : LeeWJ
# @Function  :  LeeAutoTest框架入口
# @Version  : 2.1

import inspect,time,os,sys

from app.appkeys import App
from common.NewExcel import Reader, Writer
from common.GetExcelResult import Res
from common.mail import Mail
from common.mysql import Mysql
from common.txt import Txt
from inter.interKeys import HTTP#, SOAP
from common import logger, config#, Encrypt
from web.webkeys import Web
from inter.commonKeys import sysKey


#获取当前路径
sysKey.path = sys.path[0]
logger.info(f'开始运行，当前目录路径：{sysKey.path}')

def getfunc(obj, method):
    """
    反射获取函数和参数列表
    :param obj: 对象
    :param method: 方法名
    :return:
    """
    try:
        func = getattr(obj, method)
    except Exception as e:
        return None

    arg = inspect.getfullargspec(func).__str__()
    #截取arg
    arg = arg[arg.find('args=') + 5:arg.find(', varargs')]
    #arg字符串转字典
    arg = eval(arg)
    arg.remove('self')
    return func, len(arg)

def runcase(obj, line):
    """
    用例执行
    :param obj: 对象
    :param line: 包含所有行的列表
    :return:
    """
    if len(line[0]) > 0 or len((line[1])) > 0:
        # 分组信息不执行，第一列或第二列有文字的说明是分组信息
        return

    func = getfunc(obj, line[3])
    if func is None:
        logger.warn(f'关键字{line[3]}不存在')
        return

    if func[1] == 0:
        func[0]()
    elif func[1] == 1:
        func[0](line[4])
    elif func[1] == 2:
        func[0](line[4], line[5])
    elif func[1] == 3:
        func[0](line[4], line[5], line[6])
    else:
        logger.warn("关键字暂不支持超过3个参数")


# 初始化配置
config.get_config('./lib/conf/conf.yml')
# 初始化数据库
#mysql = Mysql()
#mysql.init_mysql('./lib/conf/userinfo.sql')

print(config.config)
#要运行的用例文件名，不需要后缀名
casename = config.config.get('casename')

reader = Reader()
reader.open_excel(f'./lib/{casename}.xlsx')
writer = Writer()
#复制用例文件，用于写入结果
writer.copy_open(f'./lib/{casename}.xlsx', f'./lib/{casename}_result.xlsx')
sheetname = reader.get_sheets()

# 写开始时间
starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
writer.set_sheet(sheetname[0])
writer.write(1,3,starttime)

# 运行的实例对象，默认是HTTP接口，可选为webUI自动化，app自动化
http = HTTP(writer)
web = Web(writer)
app = App(writer)
obj = http

for sheet in sheetname:
    # 设置当前读取的sheet页面
    reader.set_sheet(sheet)
    writer.set_sheet(sheet)
    lines = reader.readline()

    # 分用例类型执行，不填则为HTTP
    line = lines[1]
    if line[1] == "HTTP":
        obj = http
    elif line[1] == "WEB":
        obj = web
    elif line[1] == "APP":
        obj = app

    for i in range(reader.rows):
        obj.row = i
        line = lines[i]
        logger.info(line)
        runcase(obj, line)


# 写结束时间
endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
writer.set_sheet(writer.get_sheets()[0])
writer.write(1,4,endtime)
writer.save_close()


# 获取结果数据
res = Res()
summary = res.get_res(f'./lib/{casename}_result.xlsx')
logger.info(summary)

#获取所有用例结果
groups = res.get_groups(f'./lib/{casename}_result.xlsx')
logger.info(groups)

#读取发邮件的html模板
txt = Txt(f"./lib/conf/{config.config['mailtxt']}")
html = txt.read()[0]

# 替换汇总信息
for key in summary.keys():
    if summary[key]=="Pass":
        html = html.replace('<td height="28" bgcolor="#FFFFFF" align="center" style="border:1px solid #ccc;">status</td>',
                     '<td height="28" bgcolor="#FFFFFF" align="center" style="border:1px solid #ccc;color:blue;">Pass</td>')
    elif summary[key]=="Fail":
        html = html.replace('<td height="28" bgcolor="#FFFFFF" align="center" style="border:1px solid #ccc;">status</td>',
                     '<td height="28" bgcolor="#FFFFFF" align="center" style="border:1px solid #ccc;color:red;">Fail</td>')
    else:
        html = html.replace(key,summary[key])

# 获取分组显示
tr = '<tr><td width="35" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">自动化类型</td><td width="70" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">用例表名</td><td width="100" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">分组信息</td><td width="50" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">用例总数</td><td width="50" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">通过数</td><td width="50" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">状态</td></tr>'
trs = ""

for i in range(len(groups)):
    try:
        tmp = tr.replace('自动化类型', str(groups[i][0]))
        tmp = tmp.replace('用例表名',str(groups[i][1]))
        tmp = tmp.replace('分组信息', str(groups[i][2]))
        tmp = tmp.replace('用例总数', str(groups[i][3]))
        tmp = tmp.replace('通过数', str(groups[i][4]))
        tmp = tmp.replace('状态', str(groups[i][5]))
    except Exception as e:
        logger.error(str(e))
    trs += tmp

html = html.replace('mailbody',trs)
mail = Mail([f'./lib/{casename}_result.xlsx'],[f'{casename}_测试报告详情.xlsx'])
mail.send(html)
