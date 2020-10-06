# @Time : 2020.7.23
# @Author : LeeWJ
# @Function  :  MYSQL模块常用功能测试流程用
# @Version  : 1.1
import pymysql

class mysql:
    def mysql(self,host,port,user,password,database,charset,sqllist):
        try:
            conn = pymysql.connect(host=host, port=port, user=user, password=password,
                                   database=database, charset=charset)
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)  #cursor=pymysql.cursors.DictCursor作用：使select查询的返回值为list中包含dict
        except Exception as e:
            #print(e)
            print(f"MYSQL连接失败:{e}")
            return 0

        try:
            for i in sqllist:
                try:
                    line = cursor.execute(i)
                    conn.commit()  # 提交数据
                    #data = cursor.fetchone()  获取当前指针的1行数据（默认指针在第一行）
                    #data = cursor.fetchmany(2)  获取下2行数据
                    data = cursor.fetchall()    # 使用fetchall()获取全部数据
                    print(data)  # 打印获取到的数据
                    print(line)   #受影响行数
                except Exception as e:
                    print(f"SQL语句执行出错，语句为：{i},报错为：:{e}")

            # 关闭游标和数据库的连接
            cursor.close()
            conn.close()

        except Exception as e:
            print(e)

#mysql调试，sqllist是要发送的sql语句列表
if __name__ == "__main__":
    config = {
    "host":"127.0.0.1",
    "port" : 3306,
    "user" : "root",
    "password" : "aaa",
    "database" : "db",
    "charset" : "utf8",
    "sqllist" : ["select * from pes_fqa","select * from test","insert test(name) values('啊啊啊')"]
    }
    m = mysql()
    m.mysql(**config)