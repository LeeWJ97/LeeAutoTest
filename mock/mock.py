# @Time : 2020/9/28 8:34 
# @Author : LeeWJ
# @Function  : flask mock独立模块，为方便框架调用，统一用get中的url参数进行交互，以json形式返回
# @Version  : 1.0

import flask,json
from flask import request

server = flask.Flask(__name__)
# 开启debug模式
server.debug = True


@server.route('/api/res',methods=['get'])
def mock1():
    '''
    原值返回
    例子：输入a=1，返回{"a":"1"}
    '''
    #将url后的请求键值对转换为字典
    jsonobj = request.args.to_dict()
    return jsonobj

@server.route('/api/md5',methods=['get'])
def mock2():
    '''
    md5原值后返回
    例子：输入a=2，返回{"a": "c81e728d9d4c2f636f067f89cc14862c"}
    '''
    jsonobj = request.args.to_dict()
    newjsonobj = dict()
    import hashlib
    for k,v in jsonobj.items():
        #字典在遍历时不能被修改，故需存储到新的变量中
        newjsonobj.update({k:hashlib.md5(v.encode(encoding='UTF-8')).hexdigest()})
    return newjsonobj



if __name__ == '__main__':
    server.run()