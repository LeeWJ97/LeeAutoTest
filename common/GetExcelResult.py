# coding:utf8

from common.NewExcel import Reader
from common import logger


class Res:
    """
    统计Excel用例执行结果信息
    """
    def __init__(self):
        # 用于记录所有模块分组信息名称
        self.summary = {}
        # 统计分组信息
        self.groups = []

    def get_res(self, result_path):
        """
            用于记录总执行结果，逻辑为，只要分组中出现一个失败用例，则认为该分组执行失败（即统计总表的数据内容）
            :param result_path: 要打开的结果文件名
            :return:统计结果
        """
        self.summary.clear()
        status = "Fail"
        # 标识是否有失败
        flag = True
        # 统计测试用例集的用例总条数
        totalcount = 0
        # 统计所有用例中通过用例的条数数
        totalpass = 0

        # 新版
        reader = Reader()
        reader.open_excel(result_path)
        reader.readline()
        line = reader.readline()[1]

        # # 旧版
        # reader = Reader()
        # reader.open_excel(result_path)
        # reader.readline()
        # line = reader.readline()
        print(line)
        self.summary['runtype'] = line[1]
        self.summary['title'] = line[2]
        self.summary['starttime'] = line[3]
        self.summary['endtime'] = line[4]
        # 获取所有sheet页面
        for n in reader.get_sheets():
            # logger.info(n)
            # 从第一个页面开始解析
            reader.set_sheet(n)
            # 获取sheet的行数，用来遍历
            row = reader.rows
            # 设置从第二行开始读
            reader.r = 1

            # 遍历sheet里面所有用例

            # openpyxl
            lines = reader.readline()
            for i in range(1, row):
                # 旧版
                # line = reader.readline()
                # 新版
                line = lines[i]
                logger.info(line)
                # 查找记录了分组信息的行
                # 如果第一列（分组信息）和第二列（类别或用例名）不同时为空,则不是用例，执行非用例的操作
                if not (line[0] == '' and line[1] == ''):
                    pass

                # 非用例行判断结束
                # 第一列信息和第二列信息均为空的行，即用例行，这时开始进行用例数、通过数、状态的统计。
                else:
                    # 判断执行结果列，如果为空，将flag置为false,视为该行有误，不纳入用例数量计算
                    if len(line) <8 or line[7] == '':
                        flag = False
                    # 执行结果不为空，则将用例统计数自增
                    else:
                        totalcount = totalcount + 1
                        # logger.info(line)
                        # 如果通过，则通过数和总通过数均自增
                        if line[7] == "PASS":
                            totalpass += 1
                        else:
                            # 出现了用例执行结果不是PASS的情况，则视为当前分组执行失败。
                            flag = False
            # for循环结束

        # 所有用例执行概况
        # logger.info(totalpass)
        # 计算执行通过率
        if flag:
            status = "Pass"

        # 计算通过率
        try:
            p = int(totalpass * 10000 / totalcount)
            passrate = p / 100
            passrate = f'{passrate}%'
        except Exception as e:
            passrate = 0.0
            logger.exception(e)

        # 用例总数
        self.summary["casecount"] = str(totalcount)
        # 通过率
        self.summary["passrate"] = str(passrate)
        self.summary['status'] = status
        # logger.info(self.summary)
        return self.summary

    def get_groups(self, result_path):
        """
            用于记录执行结果，逻辑为，只要分组中出现一个失败用例，则认为该分组执行失败，与flag联合使用。
            :param result_path: 要打开的结果文件名
            :return:所有用例结果
        """
        self.groups.clear()
        # 每一个分组统计信息为列表
        groupinfo = []

        status = "Fail"
        # 标识是否有失败
        flag = True

        # 统计每一个分组的用例总条数
        totalcount = 0
        # 统计分组用例中通过用例的条数数
        totalpass = 0

        reader = Reader()
        reader.open_excel(result_path)
        # 获取所有sheet页面
        for n in reader.get_sheets():
            # logger.info(n)
            # 从第一个页面开始解析
            reader.set_sheet(n)
            # 获取sheet的行数，用来遍历
            row = reader.rows
            # 设置从第二行开始读
            reader.r = 1

            # 标识一个分组是否统计完
            gflag = True

            # 遍历sheet里面所有用例
            # openpyxl
            lines=reader.readline()

            for i in range(1, row):

                # 旧版
                # line = reader.readline()
                # 新版
                line = lines[i]
                logger.info(line)
                # 查找记录了分组信息的行
                # 如果第一列（分组信息）
                if not line[0] == '':
                    # 先保存上一步信息
                    # 如果不是sheet最开始，就保存上一个分组统计的全部信息
                    if not gflag:
                        if flag:
                            #status = 'Pass'
                            status = '<span style="color:blue">Pass</span>'
                        else:
                            #status = 'Fail'
                            status = '<span style="color:red">Fail</span>'
                        groupinfo.append(totalcount)
                        groupinfo.append(totalpass)
                        groupinfo.append(status)
                        self.groups.append(groupinfo)

                        # 重置下一个分组的统计信息
                        # 每一个分组统计信息为列表
                        groupinfo = []
                        status = "Fail"
                        # 标识是否有失败
                        flag = True

                        # 统计每一个分组的用例总条数
                        totalcount = 0
                        # 统计分组用例中通过用例的条数数
                        totalpass = 0

                    #用例自动化类型
                    if lines[1][1]:
                        groupinfo.append(lines[1][1])
                    else :
                        groupinfo.append('HTTP')
                    # 每一个用例所在的用例表名
                    groupinfo.append(n)
                    # 保存分组名字
                    groupinfo.append(line[0])

                    # 表示当前分组未统计完
                    gflag = False
                # 第二列（类别或用例名）不同时为空,则不是用例，执行非用例的操作
                elif not line[1] == '':
                    # 不做统计
                    pass

                # 非用例行判断结束
                # 第一列信息和第二列信息均为空的行，即用例行，这时开始进行用例数、通过数、状态的统计。
                else:
                    # 判断执行结果列，如果为空，将flag置为false,视为该行有误，不纳入用例数量计算
                    if len(line) < 7 or line[7] == '':
                        flag = False
                    # 执行结果不为空，则将用例统计数自增
                    else:
                        totalcount = totalcount + 1
                        # logger.info(line)
                        # 如果通过，则通过数和总通过数均自增
                        if line[7] == "PASS":
                            totalpass += 1
                        else:
                            # 出现了用例执行结果不是PASS的情况，则视为当前分组执行失败。
                            flag = False

            # 当一个sheet统计完成后，保存上一次统计的结果
            if flag:
                #status = 'pass'
                status = '<span style="color:blue">Pass</span>'
            else:
                #status = 'fail'
                status = '<span style="color:red">Fail</span>'

            if len(groupinfo)==0:
                groupinfo.append('用例数据错误')
            groupinfo.append(totalcount)
            groupinfo.append(totalpass)
            groupinfo.append(status)
            self.groups.append(groupinfo)

            # 重置下一个分组的统计信息
            # 每一个分组统计信息为列表
            groupinfo = []
            status = "Fail"
            # 标识是否有失败
            flag = True

            # 统计每一个分组的用例总条数
            totalcount = 0
            # 统计分组用例中通过用例的条数数
            totalpass = 0

        return self.groups



if __name__ == '__main__':
    res = Res()
    s = res.get_res('../lib/HTTP接口用例_result.xls')
    print(s)
    r = res.get_groups('../lib/HTTP接口用例_result.xls')
    print(r)
