		LeeAutoTest是一款基于Python的关键字数据驱动自动化测试框架，支持HTTP接口/WEBUI/APP自动化测试，扩展性良好。Readme详细在线文档请访问：<a href='https://jmlin.cn/LAT/README.html' target='_blank'>在线文档</a>

## 一、框架简易流程图

![img](https://jmlin.cn/LAT/easyreadme.png)

## 二、配置介绍

### 2.1 conf.yml

​		框架重要配置文件。

```yml
##############用例执行配置###############
casename: 输入存储用例的xlsx文件，无需输入后缀名
##############appium的main.js文件路径###############
appium_mainjs_path: appium的main.js文件路径
################mysql配置################
mysqluser: 数据库用户名
mysqlpassword: 数据库密码
mysqlport: 数据库端口
mysqlhost: 数据库IP
mysqldb: 所使用的数据库
mysqlcharset: 数据库编码，一般utf8
################邮件配置##################
mail: 发送邮件通知的邮箱
pwd: 邮箱密码，QQ邮箱为专用授权码
mailto: 收件人，多个的话用逗号隔开
mailcopy: 抄送，多个的话用逗号隔开
mailtitle: LeeAutoTest自动化测试报告
mail_encoding: utf8
mailtxt: module1.html
mailnick: LeeAutoTest
```



## 三、用例表格文件介绍

​		目前版本由于使用openpyxl读取excel文件，故仅支持xlsx表格。各自动化模式关键字说明如下图所示：

### 3.1 HTTP接口自动化文档

![img](https://jmlin.cn/LAT/interdoc.png)



### 3.2 WEBUI自动化文档

![img](https://jmlin.cn/LAT/webdoc.png)



### 3.3 APP自动化文档

![img](https://jmlin.cn/LAT/APPdoc.png)



## 四、简易运行案例

### 4.1 邮件发送报告

<img src="https://jmlin.cn/LAT/example/mailexample.jpg" alt="img" style="zoom:30%;" />

### 4.2 HTTP接口详情

![img](https://jmlin.cn/LAT/example/interexample.png)



### 4.3 WEBUI详情

![img](https://jmlin.cn/LAT/example/webexample.png)



### 4.4 APP详情

![img](https://jmlin.cn/LAT/example/appexample.png)



## 五、框架可扩展性

​		框架具有良好可扩展性，可于相应类中添加需扩展方法，或于mock（flask）中简单添加方法逻辑，通过访问mock接口进行数据特殊处理。

